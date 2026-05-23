// === 伪代码 === //
package com.freshmart.order.controller;

@RestController
@RequestMapping("/v1/order")
class OrderController {

    @Resource OrderService orderService;
    @Resource PaymentService paymentService;
    @Resource RefundService refundService;

    /** 创建订单 — 见积木 order_create */
    @PostMapping("/create")
    BaseResponse<OrderDTO> create(@RequestBody CreateOrderRequest req) {
        return BaseResponse.ok(orderService.createOrder(req));
    }

    /** 发起支付 — 见积木 order_pay */
    @PostMapping("/pay")
    BaseResponse<PayDTO> pay(@RequestBody PayRequest req) {
        return BaseResponse.ok(paymentService.pay(req));
    }

    /** 微信支付回调 — 见积木 order_pay step 7 */
    @PostMapping("/pay/callback")
    BaseResponse<Void> payCallback(@RequestBody WxPayCallback callback) {
        paymentService.onPaySuccess(callback);
        return BaseResponse.ok();
    }

    /** 申请退款 — 见积木 order_refund */
    @PostMapping("/refund")
    BaseResponse<Void> refund(@RequestBody RefundRequest req) {
        refundService.applyRefund(req);
        return BaseResponse.ok();
    }

    @GetMapping("/{orderNo}")
    BaseResponse<OrderDTO> detail(@PathVariable String orderNo) {
        return BaseResponse.ok(orderService.findByOrderNo(orderNo));
    }
}
