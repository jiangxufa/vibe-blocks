// === 伪代码 === //
// 仅用于演示 vibe-blocks 积木如何映射到真实代码结构。
package com.freshmart.member.controller;

@RestController
@RequestMapping("/v1/member")
class MemberController {

    @Resource MemberService memberService;

    // 会员注册（mini-server 调用）
    @PostMapping("/register")
    BaseResponse<Long> register(@RequestBody RegisterRequest req) {
        Long memberId = memberService.register(req);
        return BaseResponse.ok(memberId);
    }

    // 查询会员（订单服务下单时调用）
    @GetMapping("/{memberId}")
    BaseResponse<MemberDTO> get(@PathVariable Long memberId) {
        return BaseResponse.ok(memberService.findById(memberId));
    }

    // 扣减积分（订单支付成功后调用）
    @PostMapping("/points/deduct")
    BaseResponse<Void> deductPoints(@RequestBody DeductPointsRequest req) {
        memberService.deductPoints(req.memberId, req.points, req.bizNo);
        return BaseResponse.ok();
    }

    // 累加积分（订单完成后调用）
    @PostMapping("/points/add")
    BaseResponse<Void> addPoints(@RequestBody AddPointsRequest req) {
        memberService.addPoints(req.memberId, req.points, req.bizNo);
        return BaseResponse.ok();
    }

    // 退还积分（订单退款时调用）
    @PostMapping("/points/refund")
    BaseResponse<Void> refundPoints(@RequestBody RefundPointsRequest req) {
        memberService.refundPoints(req.memberId, req.points, req.orderNo);
        return BaseResponse.ok();
    }
}
