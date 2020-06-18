import datetime

from CTFd.models import db
from .models import WhaleConfig, WhaleContainer


class DBConfig(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configs = WhaleConfig.query.all()
        for c in configs:
            self[str(c.key)] = str(c.value)

    def get(self, k, default=""):
        if k not in self:
            DBConfig.set_config(k, default)
            self[k] = default
        return self[k]

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        DBConfig.set_config(key, value)
        self[key] = value

    @staticmethod
    def get_config(key, default=""):
        result = WhaleConfig.query.filter_by(key=key).first()
        if not result:
            DBConfig.set_config(key, default)
            return default
        return result.value

    @staticmethod
    def set_config(key, value):
        DBConfig.set_all_configs({key: value})

    @staticmethod
    def get_all_configs():
        return DBConfig()

    @staticmethod
    def set_all_configs(configs):
        for c in configs:
            q = db.session.query(WhaleConfig)
            q = q.filter(WhaleConfig.key == c[0])
            record = q.one_or_none()

            if record:
                record.value = c[1]
                db.session.commit()
            else:
                config = WhaleConfig(key=c[0], value=c[1])
                db.session.add(config)
                db.session.commit()
        db.session.close()


class DBContainer:
    @staticmethod
    def create_container_record(user_id, challenge_id, port=0):
        container = WhaleContainer(user_id=user_id, challenge_id=challenge_id, port=port)
        db.session.add(container)
        db.session.commit()

        return container

    @staticmethod
    def get_current_containers(user_id):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.user_id == user_id)
        return q.first()

    @staticmethod
    def get_container_by_port(port):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.port == port)
        return q.first()

    @staticmethod
    def remove_container_record(user_id):
        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.user_id == user_id)
        q.delete()
        db.session.commit()
        db.session.close()

    @staticmethod
    def get_all_expired_container():
        timeout = int(DBConfig.get_config("docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.start_time < datetime.datetime.now() - datetime.timedelta(seconds=timeout))
        return q.all()

    @staticmethod
    def get_all_alive_container():
        timeout = int(DBConfig.get_config("docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.start_time >= datetime.datetime.now() - datetime.timedelta(seconds=timeout))
        return q.all()

    @staticmethod
    def get_all_container():
        q = db.session.query(WhaleContainer)
        return q.all()

    @staticmethod
    def get_all_alive_container_page(page_start, page_end):
        timeout = int(DBConfig.get_config("docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.start_time >= datetime.datetime.now() - datetime.timedelta(seconds=timeout))
        q = q.slice(page_start, page_end)
        return q.all()

    @staticmethod
    def get_all_alive_container_count():
        timeout = int(DBConfig.get_config("docker_timeout", "3600"))

        q = db.session.query(WhaleContainer)
        q = q.filter(WhaleContainer.start_time >= datetime.datetime.now() - datetime.timedelta(seconds=timeout))
        return q.count()
