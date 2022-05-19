import logging
import os
from telnetlib import Telnet

import paramiko

logging.getLogger(__name__)


class U2020Api(Telnet):
    def __init__(
        self,
        ftp_auth: tuple,
        nbi_auth: tuple,
        oss_name: str,
        oss_ip: str,
        ftp_port: int,
        nbi_port: int,
        dict_with_files: dict,
    ):
        super().__init__()
        self.path = os.path.normpath(os.path.dirname(__file__))  # path
        self.ftp_auth = ftp_auth  # tuple with first login and second password for ftp
        self.nbi_auth = nbi_auth  # tuple with first login and second password for nbi
        self.oss_name = oss_name  # str name
        self.oss_ip = oss_ip  # str ip
        self.ftp_port = ftp_port  # int ftp port
        self.nbi_port = nbi_port  # int nbi port
        self.files_dict = dict_with_files  # dict of mml files with key - file_name and value - file_path

    def auto(self, nbi_connect_timeout=60, nbi_command_timeout=3600):
        self.upload_to_oss()
        self.execute_on_oss(
            connect_timeout=nbi_connect_timeout, command_timeout=nbi_command_timeout
        )
        self.download_from_oss()

    def upload_to_oss(self):
        path_to_scripts_on_oss = (
            "/export/home/sysm/ftproot/itf_n/nms_mml_server/script/"
        )
        try:
            with paramiko.Transport(self.oss_ip, self.ftp_port) as transport:
                transport.connect(None, self.ftp_auth[0], self.ftp_auth[1])
                sftp = paramiko.SFTPClient.from_transport(transport)
                logging.info(f"Success Connect on SFTP to {self.oss_name}")
                try:
                    for file_name, file_path in self.files_dict.items():
                        sftp.put(file_path, path_to_scripts_on_oss + file_name)
                    sftp.close()
                    transport.close()
                    
                except Exception as error:
                    logging.critical(
                        f"Exception in upload_to_oss U2020Api in For Cycle, "
                        f"file_name:{file_name}, file_path:{file_path}, error: {error}"
                    )
                    if sftp:
                        sftp.close()
                        
                    if transport:
                        transport.close()
                        
        except Exception as error:
            logging.critical(f"Exception in upload_to_oss U2020Api: {error}")
            if sftp:
                sftp.close()
                
            if transport:
                transport.close()

    def download_from_oss(self):
        user_name = self.nbi_auth[0]  # user name for search necessary result files
        oss_result_path = "/export/home/sysm/ftproot/itf_n/nms_mml_server/result/"
        local_result_path = f"{self.path}\\Result\\{self.oss_name}"
        # paramiko.util.log_to_file(f"{os.path.normpath(os.path.dirname(__file__))}\\ftp.log")
        try:
            with paramiko.Transport(self.oss_ip, self.ftp_port) as transport:
                transport.connect(None, self.ftp_auth[0], self.ftp_auth[1])
                sftp = paramiko.SFTPClient.from_transport(transport)
                logging.info(f"Success Connect on SFTP to {self.oss_name}")
                list_dir = sftp.listdir(oss_result_path)
                string_list_dir = " ".join(list_dir)
                if user_name in string_list_dir:
                    os.makedirs(local_result_path)
                try:
                    for result_file in list_dir:
                        if (
                            result_file.find(user_name) != -1
                            and result_file.find(".rstprocess") == -1
                        ):
                            sftp.get(
                                f"{oss_result_path}{result_file}",
                                f"{local_result_path}\\{result_file}",
                            )
                            logging.info(f"Success Download File {result_file}")
                    sftp.close()
                    transport.close()
                    
                except Exception as error:
                    logging.critical(
                        f"Exception in download_from_oss U2020Api in For Cycle, "
                        f"result_file:{result_file}, local_result_path:{local_result_path}, "
                        f"oss_result_path:{oss_result_path}, error: {error}"
                    )
                    if sftp:
                        sftp.close()
                        
                    if transport:
                        transport.close()
                        
        except Exception as error:
            logging.critical(f"Exception in download_from_oss U2020Api: {error}")
            if sftp:
                sftp.close()
                
            if transport:
                transport.close()

    def execute_on_oss(self, connect_timeout: int, command_timeout: int):
        login_nbi = f'LGI:OP="{self.nbi_auth[0]}", PWD="{self.nbi_auth[1]}";'
        logout_nbi = f'LGO:OP="{self.nbi_auth[0]}";'
        finish = "---    END"
        success = "Success"
        answers_u2020 = []
        answers = ""
        try:
            self.open(self.oss_ip, self.nbi_port, timeout=connect_timeout)
            self.write(login_nbi.encode("ascii") + "\r\n".encode("ascii"))
            answer = self.read_until(finish.encode("ascii"), timeout=connect_timeout)
            answer = answer.decode("ascii")
            answers += answer
            if answer.find(success) != -1:
                logging.info(f"{self.oss_name} Login Success")
                
            else:
                logging.critical(
                    f"Else in telnet_nbi U2020Api not Find Success by {self.oss_name}"
                )
                logging.info(f"Answers: {answers}")
                self.close()
                
                return
            
        except Exception as error:
            logging.critical(f"Exception in telnet_nbi U2020Api Can not Login: {error}")
            logging.info(f"Answers: {answers}")
            self.close()
            
            return
        try:
            for file_name in self.files_dict.keys():
                activation = 'S_ACTIVATE: FILE = "' + file_name + '";'
                self.write(activation.encode("ascii") + "\r\n".encode("ascii"))
                answer = self.read_until(
                    finish.encode("ascii"), timeout=command_timeout
                )
                answer = answer.decode("ascii")
                answers += answer
                if answer.find(success) != -1:
                    logging.info(f"Find Success in Result of {file_name}")
                    
                else:
                    logging.info(f"Find Failure in Result of {file_name}")
                answers_u2020 += [answer]
                
        except Exception as error:
            logging.critical(
                f"Exception in telnet_nbi U2020Api Can not Activate Files Diction {self.files_dict} \n {error}"
            )
            logging.info(f"Answers: {answers}")
            self.close()
            
            return
        
        try:
            self.write(logout_nbi.encode("ascii") + "\r\n".encode("ascii"))
            answer = self.read_until(finish.encode("ascii"), timeout=connect_timeout)
            answer = answer.decode("ascii")
            answers += answer
            if answer.find(success) != -1:
                logging.info(f"Successful Disconnect from {self.oss_name}")
                
            else:
                logging.info(f"Can not Disconnect from {self.oss_name}")
                logging.info(f"Answers: {answers}")
                
            self.close()
            logging.info(f"List of All Answers U2020: {answers_u2020}")
            
        except Exception as error:
            logging.critical(
                f"Exception in telnet_nbi U2020Api Can not Logout: {error}"
            )
            logging.info(f"Answers: {answers}")
            self.close()
            
            return
