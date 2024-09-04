from abc import ABC, abstractmethod
import importlib
import inspect
import os
from app.models import UpgradeManifest
from sqlmodel import SQLModel, Session, select
from sqlalchemy import inspect as sqlalchemy_inspect

class UpgradeBase(ABC):
    def __init__(self, session: Session):
        self.__session = session
        
    @abstractmethod
    def upgrade(self):
        pass

class UpgradeManager:
    def __init__(self, session: Session):
        self.session = session
        self.upgrades: list[(str, UpgradeBase)] = []
        self.manifest: list[UpgradeManifest] = []
        self.load_manifest()
        self.load_upgrades()
        
    def load_manifest(self):
        inspector = sqlalchemy_inspect(self.session.get_bind())
        if not inspector.has_table("upgrademanifest"):
            print("Manifest table does not exist. Creating it...")
            SQLModel.metadata.create_all(self.session.get_bind(), tables=[UpgradeManifest.__table__])
        statement = select(UpgradeManifest)
        self.manifest = self.session.exec(statement).all()
    
    def load_upgrades(self):
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        for filename in os.listdir(scripts_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filename_without_extension = filename[:-3]
                module_name = f"app.upgrade.scripts.{filename_without_extension}" 
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, UpgradeBase) and obj != UpgradeBase:
                        upgrade_instance = obj(self.session)
                        self.upgrades.append((filename_without_extension, upgrade_instance))
    
    def run_upgrades(self):
        for upgrade in [upgrade for upgrade in self.upgrades if upgrade[0] not in [manifest.script for manifest in self.manifest]]:
            print(f"Running upgrade: {upgrade.__class__.__name__}")
            upgrade[1].upgrade(self.session)
            self.session.add(UpgradeManifest(script=upgrade[0]))
        self.session.commit()
