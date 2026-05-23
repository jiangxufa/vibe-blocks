// === 伪代码 === //
package com.freshmart.promotion.controller;

@RestController
@RequestMapping("/v1/promotion")
class PromotionController {

    @Resource CouponService couponService;
    @Resource ActivityService activityService;

    /** 创建优惠券模板 — admin-server 调用，见积木 coupon_create */
    @PostMapping("/coupon/template")
    BaseResponse<Long> createTemplate(@RequestBody CreateCouponRequest req) {
        return BaseResponse.ok(couponService.createTemplate(req));
    }

    /** 用户领券 — mini-server 调用，见积木 coupon_receive */
    @PostMapping("/coupon/receive")
    BaseResponse<Long> receive(@RequestBody ReceiveCouponRequest req) {
        return BaseResponse.ok(couponService.receive(req.memberId, req.templateId));
    }

    /** 校验并锁定券（下单时）— order-service 调用 */
    @PostMapping("/coupon/lock")
    BaseResponse<CouponLockResult> lockCoupon(@RequestBody LockCouponRequest req) {
        return BaseResponse.ok(couponService.lock(req.couponId, req.orderNo, req.amount));
    }

    /** 核销券（支付成功）— 见积木 order_pay step 6 */
    @PostMapping("/coupon/use")
    BaseResponse<Void> useCoupon(@RequestBody UseCouponRequest req) {
        couponService.useCoupon(req.couponId, req.orderNo);
        return BaseResponse.ok();
    }

    /** 释放券（订单取消/超时）— 见积木异常路径 */
    @PostMapping("/coupon/release")
    BaseResponse<Void> releaseCoupon(@RequestBody String orderNo) {
        couponService.release(orderNo);
        return BaseResponse.ok();
    }

    /** 退还券（退款）— 见积木 order_refund step 7 */
    @PostMapping("/coupon/refund")
    BaseResponse<Void> refundCoupon(@RequestBody String orderNo) {
        couponService.refund(orderNo);
        return BaseResponse.ok();
    }

    /** 创建营销活动 — admin-server 调用 */
    @PostMapping("/activity")
    BaseResponse<Long> createActivity(@RequestBody CreateActivityRequest req) {
        return BaseResponse.ok(activityService.create(req));
    }
}
