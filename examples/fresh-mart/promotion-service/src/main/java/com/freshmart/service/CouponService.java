// === 伪代码 === //
package com.freshmart.promotion.service;

@Service
class CouponService {

    @Resource CouponTemplateRepository tplRepo;
    @Resource CouponRepository couponRepo;
    @Resource ActivityClient activityClient;
    @Resource MQTemplate mq;

    /** 创建优惠券模板 — 见积木 coupon_create */
    @Transactional
    Long createTemplate(CreateCouponRequest req) {
        // 1. 校验：名称重复、面额合法、有效期合法
        if (tplRepo.existsByName(req.name)) {
            throw new ServiceException("券名称已存在");
        }
        if (req.discountAmount.compareTo(req.minOrderAmount) >= 0) {
            throw new ServiceException("券面额不能大于等于最低使用金额");
        }
        // 2. 创建模板
        CouponTemplate tpl = new CouponTemplate();
        tpl.name = req.name;
        tpl.type = req.type;
        tpl.discountAmount = req.discountAmount;
        tpl.minOrderAmount = req.minOrderAmount;
        tpl.totalCount = req.totalCount;
        tpl.remainCount = req.totalCount;
        tpl.validBegin = req.validBegin;
        tpl.validEnd = req.validEnd;
        tpl.status = CouponStatus.PENDING;  // 待发放
        tplRepo.save(tpl);

        // 3. 发券模板创建事件
        mq.send("coupon.template.created", new CouponTemplateCreatedEvent(tpl.id));
        return tpl.id;
    }

    /** 用户领券 — 见积木 coupon_receive */
    @Transactional
    Long receive(Long memberId, Long templateId) {
        // 1. 查模板，校验有效期与剩余数量（行锁）
        CouponTemplate tpl = tplRepo.findByIdForUpdate(templateId)
                .orElseThrow(() -> new ServiceException("券不存在"));
        if (tpl.status != CouponStatus.ACTIVE) {
            throw new ServiceException("活动未开始或已结束");
        }
        if (tpl.remainCount <= 0) {
            throw new ServiceException("券已抢光");
        }
        // 2. 单人限领校验
        long owned = couponRepo.countByMemberAndTemplate(memberId, templateId);
        if (owned >= tpl.maxPerUser) {
            throw new ServiceException("已达领取上限");
        }
        // 3. 扣模板剩余、生成用户券
        tpl.remainCount--;
        tplRepo.save(tpl);

        Coupon c = new Coupon();
        c.memberId = memberId;
        c.templateId = templateId;
        c.status = "UNUSED";
        c.validEnd = tpl.validEnd;
        couponRepo.save(c);
        return c.id;
    }

    /** 下单时锁券 — 见积木 order_create step 5 */
    @Transactional
    CouponLockResult lock(Long couponId, String orderNo, BigDecimal amount) {
        Coupon c = couponRepo.findByIdForUpdate(couponId)
                .orElseThrow(() -> new ServiceException("券不存在"));
        if (!"UNUSED".equals(c.status)) throw new ServiceException("券已使用");
        if (c.validEnd.isBefore(LocalDateTime.now())) throw new ServiceException("券已过期");
        CouponTemplate tpl = tplRepo.findById(c.templateId).orElseThrow();
        if (amount.compareTo(tpl.minOrderAmount) < 0) {
            throw new ServiceException("订单金额未达到最低使用金额");
        }
        c.status = "LOCKED";
        c.lockedOrderNo = orderNo;
        couponRepo.save(c);
        return new CouponLockResult(tpl.discountAmount);
    }

    /** 核销券（支付成功）— 见积木 order_pay step 6 */
    @Transactional
    void useCoupon(Long couponId, String orderNo) {
        Coupon c = couponRepo.findByIdForUpdate(couponId).orElseThrow();
        c.status = "USED";
        c.usedAt = LocalDateTime.now();
        couponRepo.save(c);
    }

    /** 释放券（取消/超时） */
    @Transactional
    void release(String orderNo) {
        couponRepo.findByLockedOrderNo(orderNo).ifPresent(c -> {
            c.status = "UNUSED";
            c.lockedOrderNo = null;
            couponRepo.save(c);
        });
    }

    /** 退款时退还券（仅当券未过期）— 见积木 order_refund step 7 */
    @Transactional
    void refund(String orderNo) {
        couponRepo.findByLockedOrderNo(orderNo).ifPresent(c -> {
            if (c.validEnd.isAfter(LocalDateTime.now())) {
                c.status = "UNUSED";
                c.lockedOrderNo = null;
                couponRepo.save(c);
            }
        });
    }
}
