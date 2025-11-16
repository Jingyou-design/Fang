"""党组织管理类：封装所有核心业务逻辑"""
import pandas as pd  # 新增这行（放在文件顶部的导入区）
import json
from datetime import datetime
from typing import List, Optional, Dict
import streamlit as st
import altair as alt

from .models import Student, PartyMemberInfo
from .enums import PartyMemberStatus, MaterialType
from .constants import (
    DATA_FILE_PATH, DEFAULT_ORG_NAME,
    MIN_TRAINERS_COUNT, MAX_TRAINERS_COUNT,
    INTRODUCERS_REQUIRED, PROBATION_PERIOD_DAYS,
    REVIEW_REQUIRED_COUNT, MAX_RECORD_DISPLAY
)

class PartyOrganization:
    """党组织管理核心类：处理所有业务逻辑"""

    def __init__(self, org_name: str = DEFAULT_ORG_NAME):
        self.org_name = org_name
        self.member_infos: Dict[str, PartyMemberInfo] = {}  # 学号 -> 党建信息
        self.load_data()  # 初始化时自动加载数据

    def load_data(self) -> None:
        """从JSON文件加载数据"""
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.member_infos = {
                    sid: PartyMemberInfo.from_dict(member_data)
                    for sid, member_data in data.items()
                }
            st.success(f"✅ 成功加载 {len(self.member_infos)} 条学生党建信息")
        except FileNotFoundError:
            st.info(f"📁 未找到数据文件，将创建新文件：{DATA_FILE_PATH}")
        except Exception as e:
            st.error(f"❌ 加载数据失败：{str(e)}")

    def save_data(self) -> None:
        """保存数据到JSON文件"""
        try:
            # 序列化所有对象
            data = {sid: member_info.to_dict() for sid, member_info in self.member_infos.items()}
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"❌ 保存数据失败：{str(e)}")

    # ------------------------------
    # 基础操作：新增、删除
    # ------------------------------
    def add_student(self, student: Student) -> bool:
        """新增学生党建信息"""
        if student.student_id in self.member_infos:
            st.error(f"❌ 学号 {student.student_id} 已存在党建信息，无需重复添加")
            return False

        # 创建党建信息对象并添加
        member_info = PartyMemberInfo(student)
        member_info.add_process_record("初始化党建信息", "录入系统，进入申请入党阶段")
        self.member_infos[student.student_id] = member_info
        self.save_data()
        st.success(f"✅ 成功添加 {student.name}（学号：{student.student_id}）的党建信息")
        return True

    def delete_student(self, student_id: str, operator: str, reason: str) -> bool:
        """真正执行删除（UI 不在这里做）"""


        # 执行删除
        file_path = r"student_party_data.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.pop(student_id, None)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # with st.expander("查看删除记录"):
        #     st.write(f"操作人：{operator}")
        #     st.write(f"删除原因：{reason}")
        #     st.write(f"删除时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    # ------------------------------
    # 申请入党阶段操作
    # ------------------------------
    def submit_application(self, student_id: str, content: str, operator: str) -> bool:
        """递交入党申请书"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        if member_info.status != PartyMemberStatus.APPLICATION:
            st.error(f"❌ 当前状态为 {member_info.status.value}，无法提交入党申请书")
            return False

        member_info.add_material(MaterialType.APPLICATION_FORM, content, operator)
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已成功提交入党申请书")
        return True

    def organization_talk(self, student_id: str, talker: str, record: str) -> bool:
        """记录党组织谈话"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验前置条件：需先提交申请书
        if MaterialType.APPLICATION_FORM not in member_info.materials:
            st.error(f"❌ 需先提交入党申请书，再进行党组织谈话")
            return False

        member_info.add_material(MaterialType.TALK_RECORD, record, talker)
        self.save_data()
        st.success(f"✅ 已完成对学号 {student_id} 的党组织谈话，谈话人：{talker}")
        return True

    # ------------------------------
    # 入党积极分子阶段操作
    # ------------------------------
    def confirm_active_member(self, student_id: str, recommenders: List[str], operator: str) -> bool:
        """确定为入党积极分子"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验前置条件
        if member_info.status != PartyMemberStatus.APPLICATION:
            st.error(f"❌ 当前状态为 {member_info.status.value}，无法确定为入党积极分子")
            return False
        if MaterialType.TALK_RECORD not in member_info.materials:
            st.error(f"❌ 需先完成党组织谈话，再确定入党积极分子")
            return False

        # 记录推荐人并更新状态
        member_info.extra_info["recommenders"] = recommenders
        member_info.update_status(
            PartyMemberStatus.ACTIVE_MEMBER,
            operator,
            remark=f"经支委会讨论，确定为入党积极分子，推荐人：{','.join(recommenders)}"
        )
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已确定为入党积极分子")
        return True

    def assign_trainer(self, student_id: str, trainers: List[str], operator: str) -> bool:
        """指定培养联系人"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验条件
        if member_info.status != PartyMemberStatus.ACTIVE_MEMBER:
            st.error(f"❌ 当前状态为 {member_info.status.value}，仅入党积极分子可指定培养联系人")
            return False
        if not (MIN_TRAINERS_COUNT <= len(trainers) <= MAX_TRAINERS_COUNT):
            st.error(f"❌ 培养联系人需{MIN_TRAINERS_COUNT}-{MAX_TRAINERS_COUNT}名正式党员，当前数量：{len(trainers)}")
            return False

        # 记录培养人
        member_info.extra_info["trainers"] = trainers
        member_info.add_process_record(
            "指定培养联系人",
            f"培养联系人：{','.join(trainers)}，操作人：{operator}"
        )
        self.save_data()
        st.success(f"✅ 已为学号 {student_id} 指定培养联系人：{','.join(trainers)}")
        return True

    def add_active_review(self, student_id: str, content: str, reviewer: str) -> bool:
        """添加积极分子考察记录"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        if member_info.status != PartyMemberStatus.ACTIVE_MEMBER:
            st.error(f"❌ 当前状态为 {member_info.status.value}，仅入党积极分子可添加考察记录")
            return False

        # 记录考察记录
        reviews = member_info.extra_info.get("active_member_reviews", [])
        reviews.append({
            "review_time": datetime.now().strftime("%Y-%m-%d"),
            "reviewer": reviewer,
            "content": content
        })
        member_info.extra_info["active_member_reviews"] = reviews
        member_info.add_process_record("添加积极分子考察记录", f"考察人：{reviewer}")
        self.save_data()
        st.success(f"✅ 已添加学号 {student_id} 的入党积极分子考察记录")
        return True

    # ------------------------------
    # 发展对象阶段操作
    # ------------------------------
    def confirm_development_object(self, student_id: str, operator: str, remark: str = "") -> bool:
        """确定为发展对象"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验条件
        if member_info.status != PartyMemberStatus.ACTIVE_MEMBER:
            st.error(f"❌ 当前状态为 {member_info.status.value}，无法确定为发展对象")
            return False

        # 校验考察记录数量
        reviews = member_info.extra_info.get("active_member_reviews", [])
        if len(reviews) < REVIEW_REQUIRED_COUNT:
            st.error(f"❌ 需经过1年以上培养考察（至少{REVIEW_REQUIRED_COUNT}次半年考察），当前考察次数：{len(reviews)}")
            return False

        # 更新状态
        member_info.update_status(PartyMemberStatus.DEVELOPMENT_OBJECT, operator, remark)
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已确定为发展对象")
        return True

    def add_political_review(self, student_id: str, content: str, reviewer: str) -> bool:
        """添加政治审查材料"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        if member_info.status != PartyMemberStatus.DEVELOPMENT_OBJECT:
            st.error(f"❌ 当前状态为 {member_info.status.value}，仅发展对象需进行政治审查")
            return False

        member_info.add_material(MaterialType.POLITICAL_REVIEW, content, reviewer)
        self.save_data()
        st.success(f"✅ 已添加学号 {student_id} 的政治审查材料")
        return True

    def assign_introducers(self, student_id: str, introducers: List[str], operator: str) -> bool:
        """指定入党介绍人"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验条件
        if member_info.status != PartyMemberStatus.DEVELOPMENT_OBJECT:
            st.error(f"❌ 当前状态为 {member_info.status.value}，仅发展对象可指定入党介绍人")
            return False
        if len(introducers) != INTRODUCERS_REQUIRED:
            st.error(f"❌ 入党介绍人需{INTRODUCERS_REQUIRED}名正式党员，当前数量：{len(introducers)}")
            return False

        # 记录介绍人
        member_info.extra_info["introducers"] = introducers
        member_info.add_process_record(
            "指定入党介绍人",
            f"入党介绍人：{','.join(introducers)}，操作人：{operator}"
        )
        self.save_data()
        st.success(f"✅ 已为学号 {student_id} 指定入党介绍人：{','.join(introducers)}")
        return True

    # ------------------------------
    # 预备党员阶段操作
    # ------------------------------
    def confirm_probationary_member(self, student_id: str, vote_result: str, operator: str) -> bool:
        """接收为预备党员"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验条件
        if member_info.status != PartyMemberStatus.DEVELOPMENT_OBJECT:
            st.error(f"❌ 当前状态为 {member_info.status.value}，无法接收为预备党员")
            return False

        # 校验必备材料
        required_materials = [
            MaterialType.POLITICAL_REVIEW,
            MaterialType.TRAINING_CERTIFICATE,
            MaterialType.PARTY_INTRODUCER
        ]
        missing = [mt.value for mt in required_materials if mt not in member_info.materials]
        if missing:
            st.error(f"❌ 缺少必备材料：{','.join(missing)}，无法接收为预备党员")
            return False

        # 记录表决结果并更新状态
        member_info.extra_info["vote_result"] = vote_result
        member_info.update_status(
            PartyMemberStatus.PROBATIONARY_MEMBER,
            operator,
            remark=f"支部大会表决通过，接收为预备党员，表决结果：{vote_result}"
        )
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已接收为预备党员")
        return True

    def hold_oath_ceremony(self, student_id: str, oath_date: str, operator: str) -> bool:
        """记录入党宣誓"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        if member_info.status != PartyMemberStatus.PROBATIONARY_MEMBER:
            st.error(f"❌ 当前状态为 {member_info.status.value}，仅预备党员需进行入党宣誓")
            return False

        # 记录宣誓信息
        member_info.add_material(
            MaterialType.OATH_RECORD,
            f"入党宣誓时间：{oath_date}，组织单位：{self.org_name}",
            operator
        )
        member_info.extra_info["oath_time"] = oath_date
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已完成入党宣誓，时间：{oath_date}")
        return True

    # ------------------------------
    # 正式党员阶段操作
    # ------------------------------
    def confirm_formal_member(self, student_id: str, conversion_date: str, operator: str) -> bool:
        """按期转为正式党员"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return False

        # 校验条件
        if member_info.status != PartyMemberStatus.PROBATIONARY_MEMBER:
            st.error(f"❌ 当前状态为 {member_info.status.value}，无法转为正式党员")
            return False

        # 校验宣誓时间
        oath_time = member_info.extra_info.get("oath_time")
        if not oath_time:
            st.error(f"❌ 未记录入党宣誓时间，无法办理转正")
            return False

        # 校验预备期
        try:
            oath_dt = datetime.strptime(oath_time, "%Y-%m-%d")
            conversion_dt = datetime.strptime(conversion_date, "%Y-%m-%d")
            if (conversion_dt - oath_dt).days < PROBATION_PERIOD_DAYS:
                st.error(f"❌ 预备期未满{PROBATION_PERIOD_DAYS}天（当前：{(conversion_dt - oath_dt).days}天），无法转正")
                return False
        except ValueError:
            st.error(f"❌ 日期格式错误，请输入 YYYY-MM-DD 格式")
            return False

        # 更新状态
        member_info.extra_info["conversion_time"] = conversion_date
        member_info.extra_info["party_age_start"] = conversion_date
        member_info.update_status(
            PartyMemberStatus.FORMAL_MEMBER,
            operator,
            remark=f"预备期已满，按期转为正式党员，党龄起算日：{conversion_date}"
        )
        self.save_data()
        st.success(f"✅ 学号 {student_id} 已按期转为正式党员，党龄起算日：{conversion_date}")
        return True

    # ------------------------------
    # 查询与统计功能
    # ------------------------------
    def query_member(self, student_id: str) -> Optional[PartyMemberInfo]:
        """查询学生党建信息（可视化展示）"""
        member_info = self._get_member_info(student_id)
        if not member_info:
            return None

        # 卡片式展示基础信息
        st.subheader(f"📋 学生党建信息详情")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**学号**：{member_info.student.student_id}")
            st.write(f"**姓名**：{member_info.student.name}")
            st.write(f"**院系**：{member_info.student.college}")
            st.write(f"**专业**：{member_info.student.major}")
        with col2:
            st.write(f"**年级**：{member_info.student.grade}")
            st.write(f"**联系方式**：{member_info.student.phone}")
            st.write(f"**当前状态**：{member_info.status.value}")
            st.write(f"**录入时间**：{member_info.create_time}")

        # 展开面板展示详细信息
        self._display_materials(member_info.materials)
        self._display_extra_info(member_info.extra_info)
        self._display_process_records(member_info.process_records)

        return member_info

    def statistics(self) -> None:
        """统计各阶段人数（图表展示）"""
        st.subheader(f"📊 {self.org_name} 学生党建统计")


        # 统计各阶段人数
        status_count = {status: 0 for status in PartyMemberStatus}
        for member_info in self.member_infos.values():
            status_count[member_info.status] += 1

        # 可视化图表
        status_names = [status.value for status in PartyMemberStatus]
        counts = [status_count[status] for status in PartyMemberStatus]

        # 兼容所有 Streamlit 版本的柱状图（核心修改）
        df = pd.DataFrame({
            "党员发展阶段": status_names,
            "人数": counts
        })


        # 使用Altair创建水平柱状图
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('人数:Q', title='人数'),
            y=alt.Y('党员发展阶段:N', title='发展阶段', sort='-x')
        ).properties(
            title=f"{self.org_name} 学生党建统计",
            width=600,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)

        # 统计表格
        total = len(self.member_infos)
        st.table({
            "党员发展阶段": status_names,
            "人数": counts,
            "占比": [f"{count / total * 100:.1f}%" if total else "0%" for count in counts]
        })
        st.write(f"**总计**：{total} 人")

    # ------------------------------
    # 内部辅助方法（私有）
    # ------------------------------
    def _get_member_info(self, student_id: str) -> Optional[PartyMemberInfo]:
        """获取学生党建信息（内部复用）"""
        member_info = self.member_infos.get(student_id)
        if not member_info:
            st.error(f"❌ 未找到学号 {student_id} 的党建信息")
            return None
        return member_info

    def _display_materials(self, materials: Dict[MaterialType, Dict]) -> None:
        """展示已提交材料"""
        with st.expander("📄 已提交材料", expanded=False):
            if materials:
                for mt, detail in materials.items():
                    st.write(f"• {mt.value}")
                    st.write(f"  提交时间：{detail['submit_time']}")
                    st.write(f"  审核人：{detail['reviewer']}")
                    st.write(f"  内容：{detail['content'][:50]}..." if len(
                        detail['content']) > 50 else f"  内容：{detail['content']}")
                    st.divider()
            else:
                st.info("暂无提交材料")

    def _display_extra_info(self, extra_info: Dict) -> None:
        """展示额外信息"""
        with st.expander("🔍 关键信息", expanded=False):
            if extra_info:
                for key, val in extra_info.items():
                    if key == "active_member_reviews":
                        st.write(f"• 积极分子考察记录：共{len(val)}次")
                        for idx, review in enumerate(val, 1):
                            st.write(f"  第{idx}次：{review['review_time']}（考察人：{review['reviewer']}）")
                    else:
                        st.write(f"• {key}：{val}")
            else:
                st.info("暂无关键信息")

    def _display_process_records(self, records: List[Dict]) -> None:
        """展示流程记录"""
        with st.expander(f"📝 流程记录（最近{MAX_RECORD_DISPLAY}条）", expanded=False):
            if records:
                # 倒序显示最近N条
                recent_records = records[-MAX_RECORD_DISPLAY:][::-1]
                for idx, record in enumerate(recent_records, 1):
                    st.write(f"{idx}. {record['time']} | {record['title']}")
                    st.write(f"   {record['detail']}")
                    st.divider()
            else:
                st.info("暂无流程记录")
