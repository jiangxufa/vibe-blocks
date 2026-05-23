// === 伪代码 === //
package com.freshmart.order.service;

@Service
class OrderService {

    @Resource OrderRepository orderRepo;
    @Resource ProductClient productClient;
    @Resource PromotionClient promotionClient;
    @Resource MemberClient memberClient;
    @Resource MQTemplate mq;

    /** 创建订单 — 跨 4 服务的复杂流程，见积木 order_create */
    @Transactional
    OrderDTO createOrder(CreateOrderRequest req) {
        // 1. 校验会员
        MemberDTO member = checkResponse(memberClient.get(req.memberId));

        // 2. 批量查商品 + 算金额
        List<ProductDTO> products = checkResponse(productClient.batchGet(req.productIds()));
        BigDecimal totalAmount = calcTotal(products, req.items);

        // 3. 生成订单号 + 预创建订单（status=PENDING_LOCK）
        String orderNo = OrderNoGen.next();
        Order order = buildOrder(orderNo, req, products, totalAmount);
        order.status = OrderStatus.PENDING_LOCK;
        orderRepo.save(order);

        // 4. 锁库存（远程调 product-service，30 分钟内未支付则释放）
        try {
            checkResponse(productClient.lockStock(
                    new LockStockRequest(req.items, orderNo)));
        } catch (Exception e) {
            order.status = OrderStatus.FAILED;
            orderRepo.save(order);
            throw new ServiceException("库存锁定失败：" + e.getMessage());
        }

        // 5. 锁优惠券（如有），算最终金额
        if (req.couponId != null) {
            try {
                CouponLockResult lock = checkResponse(promotionClient.lockCoupon(
                        new LockCouponRequest(req.couponId, orderNo, totalAmount)));
                order.discountAmount = lock.discountAmount;
                order.payAmount = totalAmount.subtract(lock.discountAmount);
                order.couponId = req.couponId;
            } catch (Exception e) {
                // 库存补偿：回滚之前锁定的库存
                productClient.releaseStock(new ReleaseStockRequest(orderNo));
                order.status = OrderStatus.FAILED;
                orderRepo.save(order);
                throw new ServiceException("优惠券不可用：" + e.getMessage());
            }
        } else {
            order.payAmount = totalAmount;
        }

        // 6. 订单状态 → 待支付
        order.status = OrderStatus.PENDING_PAY;
        orderRepo.save(order);

        // 7. 发延时消息：30 分钟后检查是否已支付，未支付则取消
        mq.sendDelay("order.pay.timeout", new OrderTimeoutEvent(orderNo), 30, MINUTES);

        return OrderDTO.from(order);
    }

    OrderDTO findByOrderNo(String orderNo) {
        return orderRepo.findByOrderNo(orderNo).map(OrderDTO::from)
                .orElseThrow(() -> new ServiceException("订单不存在"));
    }

    /** 订单超时未支付的取消（MQ 消费触发） */
    @Transactional
    void cancelIfTimeout(String orderNo) {
        Order order = orderRepo.findByOrderNoForUpdate(orderNo).orElseThrow();
        if (order.status != OrderStatus.PENDING_PAY) return;  // 已支付/已取消
        order.status = OrderStatus.CANCELLED;
        orderRepo.save(order);

        // 释放库存 + 释放优惠券
        productClient.releaseStock(new ReleaseStockRequest(orderNo));
        if (order.couponId != null) {
            promotionClient.releaseCoupon(orderNo);
        }
    }

    private BigDecimal calcTotal(List<ProductDTO> products, List<OrderItemRequest> items) {
        // ...
        return BigDecimal.ZERO;
    }

    private Order buildOrder(String no, CreateOrderRequest req,
                              List<ProductDTO> ps, BigDecimal total) {
        return new Order();
    }
}
