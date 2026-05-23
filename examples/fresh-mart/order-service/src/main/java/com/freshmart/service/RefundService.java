// === 伪代码 === //
package com.freshmart.order.service;

@Service
class RefundService {

    @Resource OrderRepository orderRepo;
    @Resource RefundRepository refundRepo;
    @Resource PaymentRepository paymentRepo;
    @Resource WxPayClient wxPayClient;
    @Resource ProductClient productClient;
    @Resource MemberClient memberClient;
    @Resource PromotionClient promotionClient;
    @Resource MQTemplate mq;

    /** 申请退款 — 跨 5 服务的复杂流程，见积木 order_refund */
    @Transactional
    void applyRefund(RefundRequest req) {
        // 1. 查订单 + 校验
        Order order = orderRepo.findByOrderNoForUpdate(req.orderNo)
                .orElseThrow(() -> new ServiceException("订单不存在"));
        if (order.status != OrderStatus.PAID) {
            throw new ServiceException("订单状态不允许退款");
        }
        if (refundRepo.existsByOrderNo(req.orderNo)) {
            throw new ServiceException("订单已申请退款");
        }
        Payment p = paymentRepo.findByOrderNoAndStatus(req.orderNo, PaymentStatus.SUCCESS)
                .orElseThrow(() -> new ServiceException("未找到成功支付记录"));

        // 2. 创建退款单
        Refund r = new Refund();
        r.orderNo = req.orderNo;
        r.refundNo = RefundNoGen.next();
        r.amount = order.payAmount;
        r.reason = req.reason;
        r.status = RefundStatus.PROCESSING;
        refundRepo.save(r);

        // 3. 调微信退款
        WxRefundResult wxResult;
        try {
            wxResult = wxPayClient.refund(p.prepayId, r.refundNo, r.amount);
        } catch (Exception e) {
            r.status = RefundStatus.FAILED;
            r.failReason = e.getMessage();
            refundRepo.save(r);
            throw new ServiceException("微信退款失败：" + e.getMessage());
        }

        // 4. 订单 → 已退款
        order.status = OrderStatus.REFUNDED;
        orderRepo.save(order);

        // 5. 退还库存
        productClient.refundStock(new RefundStockRequest(req.orderNo));

        // 6. 退还积分（已扣的退回 + 已返的扣回）
        if (order.usedPoints != null && order.usedPoints > 0) {
            memberClient.refundPoints(new RefundPointsRequest(
                    order.memberId, order.usedPoints, req.orderNo));
        }
        if (order.earnedPoints != null && order.earnedPoints > 0) {
            // 已经因为支付返了积分，要扣回（伪：deduct）
            memberClient.deductPoints(new DeductPointsRequest(
                    order.memberId, order.earnedPoints, req.orderNo + "_refund"));
        }

        // 7. 退券（如有，且未过期）
        if (order.couponId != null) {
            promotionClient.refundCoupon(req.orderNo);
        }

        // 8. 标记退款完成
        r.status = RefundStatus.SUCCESS;
        r.refundedAt = LocalDateTime.now();
        refundRepo.save(r);

        // 9. 发"订单已退款"消息（异步处理通知用户）
        mq.send("order.refunded", new OrderRefundedEvent(req.orderNo, order.memberId, r.amount));
    }
}
