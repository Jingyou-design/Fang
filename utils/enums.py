"""枚举类定义：统一管理固定选项"""
from enum import Enum

class PartyMemberStatus(Enum):
    """党员发展阶段枚举"""
    APPLICATION = "申请入党阶段"
    ACTIVE_MEMBER = "入党积极分子阶段"
    DEVELOPMENT_OBJECT = "发展对象阶段"
    PROBATIONARY_MEMBER = "预备党员阶段"
    FORMAL_MEMBER = "正式党员"
    REJECTED = "未通过/取消资格"

class MaterialType(Enum):
    """党建材料类型枚举"""
    APPLICATION_FORM = "入党申请书"
    TALK_RECORD = "党组织谈话记录"
    RECOMMENDATION = "党员/群团组织推荐表"
    POLITICAL_REVIEW = "政治审查材料"
    PARTY_INTRODUCER = "入党介绍人意见"
    TRAINING_CERTIFICATE = "集中培训结业证明"
    PARTY_VOLUNTEER_FORM = "入党志愿书"
    OATH_RECORD = "入党宣誓记录"
    PROBATION_REVIEW = "预备党员考察记录"
    CONVERSION_APPLICATION = "转正申请书"
    OTHER = "其他材料"