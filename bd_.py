import configparser
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

config = configparser.ConfigParser()
config.read('settings.ini')

LOGIN = config['base']['LOGIN']
PASS = config['base']['PASS']
BD_NAME = config['base']['BD_NAME']
BD_PATH = config['base']['BD_PATH']

Base = declarative_base()

class Writer(Base):
    __tablename__ = 'writer'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)
    name = sq.Column(sq.String(length=20))
    age = sq.Column(sq.Integer)
    city_id = sq.Column(sq.Integer)
    sex_id = sq.Column(sq.Integer)

class Photos(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True)
    photo_vk_id = sq.Column(sq.String, nullable=False)

class Users(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)
    name = sq.Column(sq.String(length=20))
    last_name = sq.Column(sq.String(length=20))
    photo_id = sq.Column(sq.Integer, sq.ForeignKey('photos.id'), nullable=False)
    photos = relationship(Photos, backref='user')

class Writer_users(Base):
    __tablename__ = 'writer_users'
    id = sq.Column(sq.Integer, primary_key=True)
    writer_id = sq.Column(sq.Integer, sq.ForeignKey('writer.id'), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'), nullable=False)
    show = sq.Column(sq.Boolean, default = False)
    likes = sq.Column(sq.Boolean, default = False)
    writer = relationship(Writer, backref='writer_users')
    user = relationship(Users, backref='writer_users')

def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def check_writer(writer_id):
    q = session.query(Writer).filter(Writer.vk_id == writer_id).first()
    if q:
        return True
    else:
        return False
def check_user(user_id):
    q = session.query(Users).filter(Users.vk_id == user_id).first()
    if q:
        return True
    else:
        return False

def check_count_photos(writer_id):
    subq = session.query(Users).join(Writer_users.user).filter(Writer_users.show == False).join(Writer).filter(Writer.vk_id == writer_id).subquery('photo_id')
    q = session.query(Photos).join(subq, Photos.id == subq.c.photo_id).count()
    return q

def add_writer(writer_id, writer_name, writer_age, writer_city_id, writer_sex_id):
    w = Writer(vk_id = writer_id, name = writer_name, age = writer_age, city_id = writer_city_id, sex_id = writer_sex_id)
    session.add(w)
    session.commit()

def get_writer(writer_id):
    w = session.query(Writer).filter(Writer.vk_id == writer_id).first()
    return [w.id, w.name, w.city_id, w.sex_id, w.age]


def add_writer_pair_and_photos(dict_user, writer_id):
    w = session.query(Writer).filter(Writer.vk_id == writer_id).first()
    for id_user, info_user in dict_user.items():
        if info_user[2]:
            f = Photos(photo_vk_id = (f'photo{id_user}_{info_user[2][0]},photo{id_user}_{info_user[2][1]},photo{id_user}_{info_user[2][2]}'))
            session.add(f)
            session.flush()
            session.refresh(f)
            u = Users(vk_id = id_user, name = info_user[0], last_name = info_user[1], photo_id = f.id)
            session.add(u)
            session.flush()
            session.refresh(u)
            wu = Writer_users(writer_id = w.id, user_id = u.id)
            session.add(wu)
    session.commit()

def add_new_pair_and_photos(dict_user, writer_id):
    for id_user, info_user in dict_user.items():
        if info_user[2]:
            f = Photos(photo_vk_id = (f'photo{id_user}_{info_user[2][0]},photo{id_user}_{info_user[2][1]},photo{id_user}_{info_user[2][2]}'))
            session.add(f)
            session.flush()
            session.refresh(f)
            u = Users(vk_id = id_user, name = info_user[0], last_name = info_user[1], photo_id = f.id)
            session.add(u)
            session.flush()
            session.refresh(u)
            w = session.query(Writer).filter(Writer.vk_id == writer_id).first()
            wu = Writer_users(writer_id = w.id, user_id = u.id)
            session.add(wu)
    session.commit()

def get_next_user(writer_id):
    subq = session.query(Users).join(Writer_users.user).filter(Writer_users.show == False).join(Writer).filter(Writer.vk_id == writer_id).subquery('photo_id')
    q = session.query(Photos).join(subq, Photos.id == subq.c.photo_id).first()
    if q == None:
        return False
    else:
        q2 = session.query(Users).join(Photos).filter(Photos.id == q.id).first()
        s = session.query(Writer_users).get(q2.id)
        s.show = True
        session.commit()
    return [q2.name, q2.last_name,q2.vk_id, q.photo_vk_id]
    
def user_like(writer_id,user_id):
    sq = session.query(Writer).join(Writer_users.writer).filter(Writer.vk_id == writer_id).subquery('id')
    q = session.query(Writer_users).join(Users.writer_users).join(sq, Writer_users.writer_id == sq.c.id).filter(Users.vk_id == user_id).first()
    q.likes = True
    session.commit()
    return

def show_like_list(writer_id):
    subq = session.query(Users).join(Writer_users.user).filter(Writer_users.likes == True).join(Writer).filter(Writer.vk_id == writer_id).all()
    like_list = []
    for w in subq:
        like_list.append([w.name, w.last_name, w.vk_id])
    return like_list

def clear_like_list(writer_id):
    subq = session.query(Writer).filter(Writer.vk_id == writer_id).first()
    q = session.query(Writer_users).filter(Writer_users.likes == True, Writer_users.writer_id == subq.id).update({Writer_users.likes: False}, synchronize_session=False)
    session.commit()
    return 

DSN = 'postgresql://'+LOGIN+':'+PASS+BD_PATH+BD_NAME
engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()




if __name__ == '__main__':
#     add_writer(123123123, 'ertyhjkl')
    # print(search_writer(28173))
    # for qqq in user_like(2810273, 3080899):
    #     print (qqq.id)
    # clear_like_list(2810273)
    pass
