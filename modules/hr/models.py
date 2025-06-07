# api/models.py - API 데이터 모델 및 스키마

from marshmallow import Schema, fields, validate, ValidationError

# 사용자 스키마
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['admin', 'manager', 'user', 'guest']))
    created_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# 생산 스키마
class ProductionSchema(Schema):
    id = fields.Int(dump_only=True)
    lot_number = fields.Str(required=True, validate=validate.Length(max=50))
    work_date = fields.Date(required=True)
    process = fields.Str(required=True)
    worker_id = fields.Int()
    plan_qty = fields.Int(required=True, validate=validate.Range(min=0))
    prod_qty = fields.Int(required=True, validate=validate.Range(min=0))
    defect_qty = fields.Int(validate=validate.Range(min=0))
    achievement_rate = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

# 재고 스키마
class ItemSchema(Schema):
    item_code = fields.Str(required=True, validate=validate.Length(max=20))
    item_name = fields.Str(required=True, validate=validate.Length(max=100))
    category = fields.Str()
    unit = fields.Str(default='EA')
    safety_stock = fields.Int(default=0, validate=validate.Range(min=0))
    current_stock = fields.Int(default=0, validate=validate.Range(min=0))
    unit_price = fields.Float(default=0, validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)

class StockMovementSchema(Schema):
    id = fields.Int(dump_only=True)
    movement_date = fields.Date(required=True)
    movement_type = fields.Str(required=True, validate=validate.OneOf(['in', 'out', 'adjust']))
    item_code = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    warehouse = fields.Str(default='main')
    remarks = fields.Str()
    created_at = fields.DateTime(dump_only=True)

# HR 스키마
class EmployeeSchema(Schema):
    employee_id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=50))
    name_en = fields.Str()
    gender = fields.Str(validate=validate.OneOf(['M', 'F']))
    birth_date = fields.Date()
    department = fields.Str(required=True)
    position = fields.Str(required=True)
    join_date = fields.Date(required=True)
    resignation_date = fields.Date()
    employment_type = fields.Str(default='regular', 
                                validate=validate.OneOf(['regular', 'contract', 'parttime', 'intern']))
    employment_status = fields.Str(default='active',
                                  validate=validate.OneOf(['active', 'leave', 'resigned']))
    base_salary = fields.Float(default=0, validate=validate.Range(min=0))
    mobile_phone = fields.Str()
    email = fields.Email()
    address = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class AttendanceSchema(Schema):
    id = fields.Int(dump_only=True)
    employee_id = fields.Str(required=True)
    attendance_date = fields.Date(required=True)
    check_in_time = fields.Time()
    check_out_time = fields.Time()
    attendance_type = fields.Str(default='normal',
                                validate=validate.OneOf(['normal', 'late', 'early', 'absent', 'leave', 'business']))
    overtime_hours = fields.Float(default=0, validate=validate.Range(min=0))
    remarks = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class PayrollSchema(Schema):
    payroll_id = fields.Int(dump_only=True)
    employee_id = fields.Str(required=True)
    pay_year = fields.Int(required=True)
    pay_month = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    base_salary = fields.Float(default=0)
    overtime_pay = fields.Float(default=0)
    bonus = fields.Float(default=0)
    allowances = fields.Float(default=0)
    gross_salary = fields.Float(dump_only=True)
    income_tax = fields.Float(default=0)
    health_insurance = fields.Float(default=0)
    pension = fields.Float(default=0)
    employment_insurance = fields.Float(default=0)
    net_salary = fields.Float(dump_only=True)
    pay_date = fields.Date()
    status = fields.Str(default='draft',
                       validate=validate.OneOf(['draft', 'confirmed', 'paid']))
    created_at = fields.DateTime(dump_only=True)

# 요청/응답 스키마
class PaginationSchema(Schema):
    page = fields.Int(default=1, validate=validate.Range(min=1))
    per_page = fields.Int(default=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str()
    sort_order = fields.Str(validate=validate.OneOf(['asc', 'desc']))

class FilterSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.Str()
    department = fields.Str()
    category = fields.Str()

class ResponseSchema(Schema):
    success = fields.Bool(default=True)
    message = fields.Str()
    data = fields.Raw()
    errors = fields.Dict()
    pagination = fields.Nested(PaginationSchema)

# 유효성 검사 헬퍼
def validate_request(schema_class, data):
    """요청 데이터 유효성 검사"""
    schema = schema_class()
    try:
        return schema.load(data), None
    except ValidationError as err:
        return None, err.messages

def serialize_response(schema_class, data, many=False):
    """응답 데이터 직렬화"""
    schema = schema_class(many=many)
    return schema.dump(data)
