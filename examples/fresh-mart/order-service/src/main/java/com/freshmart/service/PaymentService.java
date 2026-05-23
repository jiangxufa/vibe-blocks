// === 伪代码 === //
package com.freshmart.order.service;

@Service
class PaymentService {

    @Resource OrderRepository orderRepo;
    @Resource PaymentRepository paymentRepo;
    @Resource WxPayClient wxPayClient;
    @Resource ProductClient productClient;
    @Resource PromotionClient promotionClient;
    @Resource MemberClient memberClient;
    @Resource MQTemplate mq;

    /** 发起支付 — 见积木 order_pay */
    PayDTO pay(PayRequest req) {
        Order order = orderRepo.findByOrderNo(req.orderNo)
                .orElseThrow(() -> new ServiceException("订单不存在"));
        if (order.status != OrderStatus.PENDING_PAY) {
            throw new ServiceException("订单状态不允许支付");
        }
        // 1. 调微信预下单
        WxPayPrepayResult prepay = wxPayClient.prepay(WxPayRequest.from(order));
        // 2. 记录支付单
        Payment p = new Payment();
        p.orderNo = order.orderNo;
        p.amount = order.payAmount;
        p.channel = "WECHAT";
        p.prepayId = prepay.prepayId;
        p.status = PaymentStatus.PROCESSING;
        paymentRepo.save(p);
        return new PayDTO(prepay.prepayId, prepay.signedParams);
    }

    /** 微信支付回调 — 跨 4 服务的复杂回调，见积木 order_pay step 7+ */
    @Transactional
    void onPaySuccess(WxPayCallback callback) {
        String orderNo = callback.outTradeNo;
        Payment p = paymentRepo.findByOrderNoForUpdate(orderNo).orElseThrow();
        if (p.status == PaymentStatus.SUCCESS) return;  // 幂等

        // 1. 校验签名 + 校验金额
        if (!wxPayClient.verifySign(callback)) {
            throw new ServiceException("签名校验失败");
        }
        if (!callback.totalFee.equals(toCents(p.amount))) {
            throw new ServiceException("金额不一致");
        }

        // 2. 标记支付成功
        p.status = PaymentStatus.SUCCESS;
        p.paidAt = LocalDateTime.now();
        paymentRepo.save(p);

        // 3. 订单 → 已支付
        Order order = orderRepo.findByOrderNoForUpdate(orderNo).orElseThrow();
        order.status = OrderStatus.PAID;
        order.paidAt = LocalDateTime.now();
        orderRepo.save(order);

        // 4. 扣减库存（locked → sold）
        productClient.deductStock(new DeductStockRequest(orderNo));

        // 5. 扣积分（如使用了积分抵扣）
        if (order.usedPoints != null && order.usedPoints > 0) {
            memberClient.deductPoints(new DeductPointsRequest(
                    order.memberId, order.usedPoints, orderNo));
        }
        // 6. 核销券（如使用了券）
        if (order.couponId != null) {
            promotionClient.useCoupon(new UseCouponRequest(order.couponId, orderNo));
        }
        // 7. 发"订单已支付"消息（异步处理：返积分、发通知等）
        mq.send("order.paid", new OrderPaidEvent(orderNo, order.memberId, order.payAmount));
    }

    private long toCents(BigDecimal yuan) {
        return yuan.multiply(BigDecimal.valueOf(100)).longValue();
    }
}
