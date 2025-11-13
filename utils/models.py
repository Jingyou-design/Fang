"""数据模型类：定义核心数据结构"""
from datetime import datetime
from typing import List, Dict
from .enums import PartyMemberStatus, MaterialType

class Student:
    """学生基础信息模型"""
    def __init__(self, student_id: str, name: str, college: str, major: str, grade: str, phone: str):
        self.student_id = student_id  # 学号（唯一标识）
        self.name = name              # 姓名
        self.college = college        # 院系
        self.major = major            # 专业
        self.grade = grade            # 年级
        self.phone = phone            # 联系方式

    def to_dict(self) -> Dict:
        """对象转字典（用于序列化存储）"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "college": self.college,
            "major": self.major,
            "grade": self.grade,
            "phone": self.phone
        }

    @staticmethod
    def from_dict(data: Dict) -> "Student":
        """字典转对象（用于反序列化读取）"""
        return Student(
            student_id=data["student_id"],
            name=data["name"],
            college=data["college"],
            major=data["major"],
            grade=data["grade"],
            phone=data["phone"]
        )

class PartyMemberInfo:
    """党员发展信息模型（关联学生）"""
    def __init__(self, student: Student):
        self.student = student                          # 关联学生对象
        self.status = PartyMemberStatus.APPLICATION     # 初始状态：申请入党阶段
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 录入时间
        self.materials: Dict[MaterialType, Dict] = {}   # 已提交材料
        self.process_records: List[Dict] = []           # 流程记录
        self.extra_info: Dict = {}                      # 额外信息（推荐人、培养人等）

    def add_material(self, material_type: MaterialType, content: str, reviewer: str = "admin") -> None:
        """添加党建材料"""
        self.materials[material_type] = {
            "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": content,
            "reviewer": reviewer,
            "review_status": "已审核"
        }
        self.add_process_record(f"提交{material_type.value}", f"操作人：{reviewer}")

    def update_status(self, new_status: PartyMemberStatus, operator: str, remark: str = "") -> None:
        """更新党员发展状态"""
        old_status = self.status
        self.status = new_status
        self.add_process_record(
            f"状态变更：{old_status.value} → {new_status.value}",
            f"操作人：{operator}，备注：{remark}"
        )

    def add_process_record(self, title: str, detail: str) -> None:
        """添加流程记录"""
        self.process_records.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "detail": detail
        })

    def to_dict(self) -> Dict:
        """对象转字典（序列化）"""
        return {
            "student": self.student.to_dict(),
            "status": self.status.name,  # 存储枚举名称（便于反序列化）
            "create_time": self.create_time,
            "materials": {mt.name: val for mt, val in self.materials.items()},
            "process_records": self.process_records,
            "extra_info": self.extra_info
        }

    @staticmethod
    def from_dict(data: Dict) -> "PartyMemberInfo":
        """字典转对象（反序列化）"""
        student = Student.from_dict(data["student"])
        info = PartyMemberInfo(student)
        info.status = PartyMemberStatus[data["status"]]
        info.create_time = data["create_time"]
        info.materials = {MaterialType[mt_name]: val for mt_name, val in data["materials"].items()}
        info.process_records = data["process_records"]
        info.extra_info = data["extra_info"]
        return info