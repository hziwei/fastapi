"""  错误代码定义
     1. 错误代码规则: 由三段组成：<类别> + <系统/模块别名> + <6位错误代码>

     2. 类别定义:
        100	信息/提示性类别.如：接收请求正在处理；系统忙等
        200	结果类别.该类代码段为明确结果，包括成功或失败，同时影响业务流程的，需要重点关注
        400	客户端错误类别.一般本地环境与自身代码引起的错误。或用户数据引起的错误。
        500	服务端错误类别.服务端处理出错，税局端错误。如：网厅页面元素变化，页面变化，税局卡顿。
        300	重试性类别.需要附加操作完成的处理。一般为任务重试类错误。

     3. 别名:
        R	机器人中心任务执行	如：北京机器人 Worker
        H	硬件设备类	如：CA、SMS设备

"""

from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)


class InformationalErrorCode(StrEnum):
    """信息/提示性类别代码定义-!00R
    """

    # 报告提示信息
    REPORT_INFO_CODE = "100R000001"


class EndingErrorCode(StrEnum):
    """运行结果类错误代码定义-200R
       该类代码有很明确结果，同时影响业务流程的，结果涉及需要处理，且需重点关注。
    """

    # OK 执行成功
    EXECUTE_SUCCESS = "200R000000"

    # 未知
    UNKNOWN_ERROR = "200R009999"


class ClientErrorCode(StrEnum):
    """由客户端/用户数据引起的错误代码定义-400R
       用户提供错误数据引起的出错，或者本地环境引起出错。
    """

    # 系统错误引起失败
    EXECUTE_ERROR = "400R000001"

    # 调用API类失败
    API_INVOKE_ERROR = "400R100001"

    # 用户问题引起执行任务失败
    USER_CAUSED_ERROR = "400R002001"

    # 校验用户数据出错
    USER_PARAMETERS_INVALID_ERROR = "400R002002"


