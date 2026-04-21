"""Bridge to call Paxstore Java SDK from Python via subprocess."""

import json
import subprocess
import os
from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class TerminalApkInfo:
    """APK push record from Paxstore."""
    id: int
    package_name: str
    version_name: str
    version_code: int
    status: str
    activated_date: Optional[int] = None
    param_template_name: Optional[str] = None


@dataclass  
class SearchTerminalApkResult:
    """Result from searchTerminalApk API."""
    business_code: int
    message: Optional[str]
    total_count: int
    records: List[TerminalApkInfo]
    raw_json: dict


@dataclass
class TerminalInfo:
    """Terminal info from Paxstore."""
    id: int
    name: str
    tid: str
    serial_no: Optional[str]
    status: str
    model_name: Optional[str]
    merchant_name: Optional[str]
    reseller_name: Optional[str]


@dataclass
class SearchTerminalResult:
    """Result from searchTerminal API."""
    business_code: int
    message: Optional[str]
    total_count: int
    terminals: List[TerminalInfo]
    raw_json: dict


class PaxstoreBridge:
    """Bridge to Paxstore Java SDK."""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._classpath = None
    
    def _get_classpath(self) -> str:
        """Build classpath for Java execution."""
        if self._classpath:
            return self._classpath
            
        cp_file = os.path.join(self.project_root, "cp.txt")
        
        # Generate classpath if not exists
        if not os.path.exists(cp_file):
            subprocess.run(
                ["mvn", "dependency:build-classpath", f"-Dmdep.outputFile=cp.txt", "-q"],
                cwd=self.project_root,
                check=True,
                shell=True
            )
        
        with open(cp_file, "r") as f:
            deps = f.read().strip()
        
        target_classes = os.path.join(self.project_root, "target", "classes")
        self._classpath = f"{target_classes};{deps}"
        return self._classpath
    
    def _ensure_compiled(self):
        """Ensure Kotlin code is compiled."""
        target_classes = os.path.join(self.project_root, "target", "classes")
        if not os.path.exists(target_classes):
            subprocess.run(
                ["mvn", "compile", "-q"],
                cwd=self.project_root,
                check=True,
                shell=True
            )
    
    def search_terminal_apk(self, tid: str, package_name: str = None) -> SearchTerminalApkResult:
        """
        Search terminal APK pushes via Paxstore SDK.
        
        Args:
            tid: Terminal TID
            package_name: Optional package name filter
            
        Returns:
            SearchTerminalApkResult with totalCount and APK records
        """
        self._ensure_compiled()
        classpath = self._get_classpath()
        
        # Build command
        args = [tid]
        if package_name:
            args.append(package_name)
        
        cmd = [
            "java", "-cp", classpath,
            "com.pax.test.SearchTerminalApkJsonKt"
        ] + args
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Paxstore SDK call failed: {result.stderr}")
        
        # Parse JSON output
        raw_json = json.loads(result.stdout)
        
        records = []
        if raw_json.get("pageInfo") and raw_json["pageInfo"].get("dataSet"):
            for item in raw_json["pageInfo"]["dataSet"]:
                param_template = None
                if item.get("terminalApkParam"):
                    param_template = item["terminalApkParam"].get("paramTemplateName")
                    
                records.append(TerminalApkInfo(
                    id=item.get("id", 0),
                    package_name=item.get("apkPackageName", ""),
                    version_name=item.get("apkVersionName", ""),
                    version_code=item.get("apkVersionCode", 0),
                    status=item.get("status", ""),
                    activated_date=item.get("activatedDate"),
                    param_template_name=param_template
                ))
        
        return SearchTerminalApkResult(
            business_code=raw_json.get("businessCode", -1),
            message=raw_json.get("message"),
            total_count=raw_json.get("pageInfo", {}).get("totalCount", 0),
            records=records,
            raw_json=raw_json
        )

    def search_terminal(
        self, 
        keyword: str = "", 
        reseller_name: str = None, 
        merchant_name: str = None
    ) -> SearchTerminalResult:
        """
        Search terminals via Paxstore SDK.
        
        Args:
            keyword: Search keyword (TID, serial number, or name)
            reseller_name: Optional reseller name filter
            merchant_name: Optional merchant name filter (worldpayMID)
            
        Returns:
            SearchTerminalResult with terminals list
        """
        self._ensure_compiled()
        classpath = self._get_classpath()
        
        # Build command args
        args = [
            keyword or "",
            reseller_name or "",
            merchant_name or ""
        ]
        
        cmd = [
            "java", "-cp", classpath,
            "com.pax.test.SearchTerminalJsonKt"
        ] + args
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Paxstore SDK call failed: {result.stderr}")
        
        # Parse JSON output
        raw_json = json.loads(result.stdout)
        
        terminals = []
        if raw_json.get("pageInfo") and raw_json["pageInfo"].get("dataSet"):
            for item in raw_json["pageInfo"]["dataSet"]:
                terminals.append(TerminalInfo(
                    id=item.get("id", 0),
                    name=item.get("name", ""),
                    tid=item.get("tid", ""),
                    serial_no=item.get("serialNo"),
                    status=item.get("status", ""),
                    model_name=item.get("modelName"),
                    merchant_name=item.get("merchantName"),
                    reseller_name=item.get("resellerName")
                ))
        
        return SearchTerminalResult(
            business_code=raw_json.get("businessCode", -1),
            message=raw_json.get("message"),
            total_count=raw_json.get("pageInfo", {}).get("totalCount", 0),
            terminals=terminals,
            raw_json=raw_json
        )
