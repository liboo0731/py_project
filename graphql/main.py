from graphene import ObjectType
from graphene import InputObjectType
from graphene import Field
from graphene import ID, String, Boolean, Int, List
from graphene import Schema
from graphene import Argument


class StudentType(ObjectType):
    id = ID()
    name = String()
    sex = Boolean()
    age = Int()


class StudentInput(InputObjectType):
    id = ID()
    name = String(require=True)
    sex = Boolean()
    age = Int()


class ClassType(ObjectType):
    cid = ID()
    name = String(name=Argument(String), default_value=None)
    students = List(StudentType)

    class Meta:
        filter_fields = ['name']


class SchoolType(ObjectType):
    sid = ID()
    name = String()
    classes = List(ClassType)


class Query(ObjectType):
    student = Field(StudentType, stud=StudentInput())
    schoolclass = Field(ClassType)
    school = Field(SchoolType)

    def resolve_student(self, info, stud):
        return {"id": 1, "name": "StudentA", "sex": True, "age": 12}

    def resolve_schoolclass(self, info):
        return {"cid": 1,
                "name": "ClassA",
                "students": [
                    {"id": 1, "name": "StudentA", "sex": True, "age": 12},
                    {"id": 2, "name": "StudentB", "sex": False, "age": 14}
                ]}

    def resolve_school(self, info):
        return {"sid": 1,
                "name": "SchoolA",
                "classes": [
                    {"cid": 1,
                     "name": "ClassA",
                     "students": [
                         {"id": 1, "name": "StudentA", "sex": True, "age": 12},
                         {"id": 2, "name": "StudentB", "sex": False, "age": 14}
                     ]},
                    {"cid": 2,
                     "name": "ClassB",
                     "students": [
                         {"id": 3, "name": "StudentA", "sex": True, "age": 12},
                         {"id": 4, "name": "StudentB", "sex": False, "age": 14}
                     ]}
                ]}


if __name__ == '__main__':
    schema = Schema(query=Query)
    squery = '''
        query dosomething {
            school {
                sid,
                name,
                classes {
                    cid
                    name
                    students {
                        id
                        name
                        sex
                        age
                    }
                }
            }
        }
    '''

    cquery = '''
        query dosomething {
            schoolclass {
                cid
                name(name:"aaa")
                students {
                    id
                    name
                    sex
                    age
                }
            }
        }
    '''

    query = '''
        query dosomething {
            student(stud:{name:"ss"}) {
                id
                name
                sex
                age
            }
        }
    '''

    result = schema.execute(squery)
    print(result)

    result = schema.execute(cquery)
    print(result)

    result = schema.execute(query)
    print(result)
