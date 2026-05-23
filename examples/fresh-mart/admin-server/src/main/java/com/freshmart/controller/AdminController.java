// === 伪代码 === //
// 运营后台 BFF：管理优惠券、活动、订单退款等。
package com.freshmart.admin.controller;

@RestController
@RequestMapping("/sys")
class AdminController {

    @Resource PromotionClient promotionClient;
    @Resource OrderClient orderClient;
    @Resource MemberClient memberClient;

    /** 创建优惠券模板 — 见积木 coupon_create */
    @RequiresPermissions("coupon:add")
    @PostMapping("/coupon/template")
    BaseResponse<Long> createCouponTemplate(@RequestBody CreateCouponRequest req) {
        return promotionClient.createTemplate(req);
    }

    /** 创建营销活动 */
    @RequiresPermissions("activity:add")
    @PostMapping("/activity")
    BaseResponse<Long> createActivity(@RequestBody CreateActivityRequest req) {
        return promotionClient.createActivity(req);
    }

    /** 客服退款 — 见积木 order_refund */
    @RequiresPermissions("order:refund")
    @PostMapping("/order/refund")
    BaseResponse<Void> refundOrder(@RequestBody RefundRequest req) {
        return orderClient.refund(req);
    }

    /** 会员详情（聚合：基础信息 + 订单 + 券包） */
    @RequiresPermissions("member:view")
    @GetMapping("/member/{memberId}/profile")
    BaseResponse<MemberProfileVO> profile(@PathVariable Long memberId) {
        MemberDTO member = checkResponse(memberClient.get(memberId));
        List<OrderDTO> orders = orderClient.byMember(memberId).getData();
        List<CouponDTO> coupons = promotionClient.couponsByMember(memberId).getData();
        return BaseResponse.ok(MemberProfileVO.of(member, orders, coupons));
    }
}
