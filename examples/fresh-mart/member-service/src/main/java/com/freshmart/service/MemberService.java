// === 伪代码 === //
package com.freshmart.member.service;

@Service
class MemberService {

    @Resource MemberRepository memberRepo;
    @Resource PointsRepository pointsRepo;
    @Resource MemberLevelRepository levelRepo;
    @Resource MQTemplate mq;

    /** 会员注册 — 见积木 member_register */
    @Transactional
    Long register(RegisterRequest req) {
        // 1. 手机号唯一性校验
        if (memberRepo.existsByMobile(req.mobile)) {
            throw new ServiceException("手机号已注册");
        }
        // 2. 创建会员记录
        Member m = new Member();
        m.mobile = req.mobile;
        m.nickname = req.nickname == null ? "用户" + req.mobile.substring(7) : req.nickname;
        m.level = MemberLevel.NORMAL;
        m.points = 0L;
        memberRepo.save(m);

        // 3. 发注册事件 — 优惠券服务消费后发新人券
        mq.send("member.registered", new MemberRegisteredEvent(m.id, m.mobile));
        return m.id;
    }

    MemberDTO findById(Long memberId) {
        return memberRepo.findById(memberId).map(MemberDTO::from)
                .orElseThrow(() -> new ServiceException("会员不存在"));
    }

    /** 扣减积分 — 见积木 order_pay 的 step 5 */
    @Transactional
    void deductPoints(Long memberId, Long points, String bizNo) {
        Member m = memberRepo.findByIdForUpdate(memberId)
                .orElseThrow(() -> new ServiceException("会员不存在"));
        if (m.points < points) throw new ServiceException("积分不足");
        m.points -= points;
        memberRepo.save(m);
        pointsRepo.saveLog(memberId, -points, "deduct", bizNo);
    }

    /** 累加积分（订单完成 1% 返积分）— 见积木 order_pay */
    @Transactional
    void addPoints(Long memberId, Long points, String bizNo) {
        Member m = memberRepo.findByIdForUpdate(memberId)
                .orElseThrow(() -> new ServiceException("会员不存在"));
        m.points += points;
        memberRepo.save(m);
        pointsRepo.saveLog(memberId, points, "earn", bizNo);

        // 触发等级升级判断
        checkLevelUpgrade(m);
    }

    /** 退款时退还积分 — 见积木 order_refund step 6 */
    @Transactional
    void refundPoints(Long memberId, Long points, String orderNo) {
        Member m = memberRepo.findByIdForUpdate(memberId)
                .orElseThrow(() -> new ServiceException("会员不存在"));
        m.points += points;
        memberRepo.save(m);
        pointsRepo.saveLog(memberId, points, "refund", orderNo);
    }

    /** 等级升级判断 — 见积木 member_level_upgrade */
    private void checkLevelUpgrade(Member m) {
        MemberLevel newLevel = levelRepo.matchLevel(m.points);
        if (newLevel != m.level) {
            MemberLevel old = m.level;
            m.level = newLevel;
            memberRepo.save(m);
            mq.send("member.level.upgraded",
                    new LevelUpgradeEvent(m.id, old, newLevel));
        }
    }
}
