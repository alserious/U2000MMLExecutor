from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import threading
import logging
import secret
import api

logging.basicConfig(filename="huawei.log", filemode='a', level=logging.DEBUG,
                    format="%(asctime)s:%(threadName)s:%(levelname)s - %(message)s")
logging.getLogger(__name__)


def object_thread():
    """
    Function for working with threading like different objects
    :return:
    """
    diction_1 = {
        "MML_file1": "C:\\file1.txt",
        "MML_file2": "C:\\file2.txt"
    }
    diction_2 = {
        "MML_file3": "C:\\file3.txt",
        "MML_file4": "C:\\file4.txt"
    }
    first_thread = api.U2020Api(secret.ftp_auth, secret.nbi_auth, oss_name="first_oss", oss_ip="192.168.1.1",
                                ftp_port=22, nbi_port=31331, dict_with_files=diction_1)
    second_thread = api.U2020Api(secret.ftp_auth, secret.nbi_auth, oss_name="second_oss", oss_ip="192.168.1.2",
                                 ftp_port=22, nbi_port=31331, dict_with_files=diction_2)
    first_thread = threading.Thread(target=first_thread.auto)
    second_thread = threading.Thread(target=second_thread.auto)
    first_thread.start()
    second_thread.start()
    logging.info(f'Threads Started {datetime.now().strftime("%d.%m.%Y %H:%M")}')
    first_thread.join()
    second_thread.join()
    logging.info(f'Threads Finished {datetime.now().strftime("%d.%m.%Y %H:%M")}')


# object_thread()

def thread_function(args):
    api.U2020Api(ftp_auth=args[0], nbi_auth=args[1], oss_name=args[2], oss_ip=args[3], ftp_port=args[4],
                 nbi_port=args[5], dict_with_files=args[6]).auto()


def thread_pool():
    """
    Function for working with threading pool map the same attributes
    :return:
    """
    diction_1 = {
        "MML_file1": "C:\\file1.txt",
        "MML_file2": "C:\\file2.txt"
    }
    diction_2 = {
        "MML_file3": "C:\\file3.txt",
        "MML_file4": "C:\\file4.txt"
    }

    list = [[secret.ftp_auth, secret.nbi_auth, "first_oss", "192.168.1.1", 22, 31331, diction_1],
            [secret.ftp_auth, secret.nbi_auth, "second_oss", "192.168.1.2", 22, 31331, diction_2]]
    pool = ThreadPool(5)
    results = pool.map(target=thread_function, args=list)
    pool.close()
    pool.join()
    logging.info(results)
    logging.info(f'Threads Finished {datetime.now().strftime("%d.%m.%Y %H:%M")}')

# thread_pool()
