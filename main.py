"""学生党建信息管理系统 - 主程序入口（Streamlit界面）"""
import streamlit as st
from utils.organization import PartyOrganization
from utils.models import Student
from utils.constants import SYSTEM_NAME, SYSTEM_ICON, PAGE_LAYOUT

def main():
    # 页面基础配置
    st.set_page_config(
        page_title=SYSTEM_NAME,
        page_icon=SYSTEM_ICON,
        layout=PAGE_LAYOUT
    )

    # 初始化核心业务类
    org = PartyOrganization()

    # 页面标题与分割线
    st.title(f"{SYSTEM_ICON} {SYSTEM_NAME}")
    st.divider()

    # 侧边栏导航菜单
    with st.sidebar:
        st.header("功能导航")
        menu_option = st.radio(
            "请选择功能模块",
            [
                "1. 新增学生党建信息",
                "2. 申请入党阶段操作",
                "3. 入党积极分子阶段操作",
                "4. 发展对象阶段操作",
                "5. 预备党员阶段操作",
                "6. 正式党员阶段操作",
                "7. 查询学生党建信息",
                "8. 统计各阶段人数",
                "9. 删除学生党建信息（谨慎）"  # 确保这里是 "9. " 后1个空格
            ]
        )

    # ------------------------------
    # 1. 新增学生党建信息
    # ------------------------------
    if menu_option == "1. 新增学生党建信息":
        st.subheader("📝 新增学生党建信息")
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                name = st.text_input("姓名（必填）", placeholder="如：张三")
                college = st.text_input("院系（必填）", placeholder="如：计算机学院")
            with col2:
                major = st.text_input("专业（必填）", placeholder="如：计算机科学与技术")
                grade = st.text_input("年级（必填）", placeholder="如：2023级")
                phone = st.text_input("联系方式（必填）", placeholder="如：13800138000")

            submit_btn = st.form_submit_button("确认新增")
            if submit_btn:
                if not all([student_id, name, college, major, grade, phone]):
                    st.error("❌ 请填写所有必填项！")
                    return
                student = Student(student_id, name, college, major, grade, phone)
                org.add_student(student)

    # ------------------------------
    # 2. 申请入党阶段操作
    # ------------------------------
    elif menu_option == "2. 申请入党阶段操作":
        st.subheader("📥 申请入党阶段操作")
        tab1, tab2 = st.tabs(["递交入党申请书", "党组织谈话"])

        with tab1:
            with st.form("submit_application_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                content = st.text_area("申请书核心内容（必填）", placeholder="简要描述入党动机、个人情况等，100字以内")
                operator = st.text_input("操作人（必填）", placeholder="如：李老师")
                st.form_submit_button("确认提交") and org.submit_application(student_id, content, operator)

        with tab2:
            with st.form("talk_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                talker = st.text_input("谈话人（必填）", placeholder="如：王书记")
                record = st.text_area("谈话记录（必填）", placeholder="简要记录谈话内容，100字以内")
                st.form_submit_button("确认记录") and org.organization_talk(student_id, talker, record)

    # ------------------------------
    # 3. 入党积极分子阶段操作
    # ------------------------------
    elif menu_option == "3. 入党积极分子阶段操作":
        st.subheader("🌟 入党积极分子阶段操作")
        tab1, tab2, tab3 = st.tabs(["确定为积极分子", "指定培养联系人", "添加考察记录"])

        with tab1:
            with st.form("confirm_active_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                recommenders = st.text_input("推荐人（必填，逗号分隔）", placeholder="如：张党员,李党员")
                operator = st.text_input("操作人（必填）", placeholder="如：王支委")
                st.form_submit_button("确认确定") and org.confirm_active_member(student_id, recommenders.split(","), operator)

        with tab2:
            with st.form("assign_trainer_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                trainers = st.text_input("培养联系人（1-2人，逗号分隔）", placeholder="如：张党员,李党员")
                operator = st.text_input("操作人（必填）", placeholder="如：王支委")
                st.form_submit_button("确认指定") and org.assign_trainer(student_id, trainers.split(","), operator)

        with tab3:
            with st.form("add_review_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                content = st.text_area("考察记录（必填）", placeholder="简要记录考察情况，100字以内")
                reviewer = st.text_input("考察人（必填）", placeholder="如：张培养人")
                st.form_submit_button("确认添加") and org.add_active_review(student_id, content, reviewer)

    # ------------------------------
    # 4. 发展对象阶段操作
    # ------------------------------
    elif menu_option == "4. 发展对象阶段操作":
        st.subheader("🎯 发展对象阶段操作")
        tab1, tab2, tab3 = st.tabs(["确定为发展对象", "添加政审材料", "指定入党介绍人"])

        with tab1:
            with st.form("confirm_development_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                remark = st.text_input("备注（可选）", placeholder="如：经1年培养，基本具备党员条件")
                operator = st.text_input("操作人（必填）", placeholder="如：王支委")
                st.form_submit_button("确认确定") and org.confirm_development_object(student_id, operator, remark)

        with tab2:
            with st.form("add_political_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                content = st.text_area("政审结果（必填）", placeholder="简要记录政治审查情况，100字以内")
                reviewer = st.text_input("审查人（必填）", placeholder="如：李负责人")
                st.form_submit_button("确认添加") and org.add_political_review(student_id, content, reviewer)

        with tab3:
            with st.form("assign_introducers_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                introducers = st.text_input("入党介绍人（2人，逗号分隔）", placeholder="如：张党员,李党员")
                operator = st.text_input("操作人（必填）", placeholder="如：王支委")
                st.form_submit_button("确认指定") and org.assign_introducers(student_id, introducers.split(","), operator)

    # ------------------------------
    # 5. 预备党员阶段操作
    # ------------------------------
    elif menu_option == "5. 预备党员阶段操作":
        st.subheader("🎉 预备党员阶段操作")
        tab1, tab2 = st.tabs(["接收为预备党员", "举行入党宣誓"])

        with tab1:
            with st.form("confirm_probationary_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                vote_result = st.text_input("支部大会表决结果（必填）", placeholder="如：应到20人，实到18人，赞成18人")
                operator = st.text_input("操作人（必填）", placeholder="如：王书记")
                st.form_submit_button("确认接收") and org.confirm_probationary_member(student_id, vote_result, operator)

        with tab2:
            with st.form("oath_form", clear_on_submit=True):
                student_id = st.text_input("学号（必填）", placeholder="如：2023001")
                oath_date = st.date_input("宣誓日期（必填）").strftime("%Y-%m-%d")
                operator = st.text_input("操作人（必填）", placeholder="如：李组织委员")
                st.form_submit_button("确认记录") and org.hold_oath_ceremony(student_id, oath_date, operator)

    # ------------------------------
    # 6. 正式党员阶段操作
    # ------------------------------
    elif menu_option == "6. 正式党员阶段操作":
        st.subheader("🏆 正式党员阶段操作")
        with st.form("confirm_formal_form", clear_on_submit=True):
            student_id = st.text_input("学号（必填）", placeholder="如：2023001")
            conversion_date = st.date_input("转正日期（必填）").strftime("%Y-%m-%d")
            operator = st.text_input("操作人（必填）", placeholder="如：王书记")
            st.form_submit_button("确认转正") and org.confirm_formal_member(student_id, conversion_date, operator)

    # ------------------------------
    # 7. 查询学生党建信息
    # ------------------------------
    elif menu_option == "7. 查询学生党建信息":
        st.subheader("🔍 查询学生党建信息")
        with st.form("query_form", clear_on_submit=False):
            student_id = st.text_input("请输入学号", placeholder="如：2023001")
            if st.form_submit_button("查询"):
                if not student_id:
                    st.error("❌ 请输入学号！")
                    return
                org.query_member(student_id)

    # ------------------------------
    # 8. 统计各阶段人数
    # ------------------------------
    elif menu_option == "8. 统计各阶段人数":
        org.statistics()

    # ------------------------------
    # 9. 删除学生党建信息
    # ------------------------------
    elif menu_option == "9. 删除学生党建信息（谨慎）":  # 去掉多余的空格，和菜单文本一致
        st.subheader("⚠️ 删除学生党建信息（不可逆）")
        st.warning("仅允许删除错误录入、学生毕业/退学等场景的党建信息，请谨慎操作！")
        with st.form("delete_form", clear_on_submit=True):
            student_id = st.text_input("学号（必填）", placeholder="如：2023001")
            operator = st.text_input("操作人（必填）", placeholder="如：王书记")
            reason = st.text_input("删除原因（必填）", placeholder="如：学生退学、信息录入错误")
            st.form_submit_button("提交删除申请") and org.delete_student(student_id, operator, reason)

if __name__ == "__main__":
    main()