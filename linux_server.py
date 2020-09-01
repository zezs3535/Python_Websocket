import asyncio;
# 웹 소켓 모듈을 선언한다.
import websockets;
import socket;

#아래서부터 파일 관련 패키지
import os;
import sys;
import json;
import shutil
import string
#기본 경로
#os.chdir('D:')
os.chdir('/')
ndir=nfile=0
make_file_name=''

# 업로드 할 때 데이터 정보에 관한 클래스
class Node():
    #생성자
    def __init__(self):
        self.__filename=''; # 받는 파일의 이름
        self.__filesize =0; # 받는 파일의 크기
        self.__data='';     # 받는 파일의 내용(클라이언트에서 정한 버퍼 사이즈 만큼씩 받는다)
        self.__datasize=0;  # 받은 파일의 사이즈

    # filename getter
    @property
    def filename(self):
        return self.__filename;

    # filename setter
    @filename.setter
    def filename(self, filename):
        self.__filename=filename;

    # filesize getter
    @property
    def filesize(self):
        return self.__filesize;

    # filesize setter
    @filesize.setter
    def filesize(self, filesize):
        self.__filesize=int(filesize);

    # data getter
    @property
    def data(self):
        return self.__data;

    # data setter
    @data.setter
    def data(self, data):
        self.__data = data;

    @property
    def datasize(self):
        return self.__datasize;

    @datasize.setter
    def datasize(self, length):
        self.__datasize += length;

    # add data to self.__data
    def add_data(self, data):
        self.__data += data;

    # 파일전송이 끝났는지 확인하는 함수
    def is_completed(self):
        if self.__filesize == self.__datasize:
            print('Transfer is finished')
            return True;
        else:
            return False;
    def save(self, data):
        # 파일을 binary형식, 이어붙이는 모드로 연뒤에 파일을 계속 이어쓴다
        with open("/tmp/lvp/"+self.__filename, "ab+") as handle:
            handle.write(data);
        # 받은 datasize를 받은 데이터 size를 더해가며 저장한다(전송 종료 조건에 사용)
        self.__datasize += len(data)


# 클라이언트가 '파일 업로드'버튼을 클릭하면 호출된다.
async def file_accept(websocket, path):
    node = Node(); # node에 Node() 클래스 할당
    while True:
        # 클라이언트로부터 메시지를 대기한다.
        message = await websocket.recv();
        if message == 'START': #클라이언트로부터 'START' 메시지가 날라오면
            await websocket.send("FILENAME"); #파일 이름을 요청
        elif message == 'FILENAME': #파일 이름을 받는다
            node.filename = await websocket.recv();
            await websocket.send("FILESIZE")
        elif message == 'FILESIZE': #파일 사이즈를 받는다
            node.filesize = await websocket.recv();
            await websocket.send("DATA");#데이터를 요청한다
        elif message == 'DATA':#데이터가 오면 저장한다
            node.save(await websocket.recv());
            if node.is_completed() == False:#전송이 끝나지 않았으면 계속 전송
                await websocket.send("DATA");
            else:
                await websocket.close();#전송이 끝났으면 웹소켓을 닫고 종료
                break;

async def text_accept(websocket, path):
##    #Linux Version
##    available_drives = ['/']
##    json_dirList = json.dumps({"kinds": "directory", "list": available_drives})


    #Windows Version
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    print(available_drives)
    
    json_dirList = json.dumps({"kinds": "directory", "list": available_drives})
    targetLink=''
    #드라이블 경로로 가기 위해서는 C: 이 아닌 C:\ 이렇게 필요해서 끝에 \를 붙여줌
    for i in range(len(available_drives)):
        available_drives[i] = available_drives[i] + '\\'
        print(available_drives[i])
    #Windows Version
        
    
    await websocket.send("{}".format(json_dirList))
    global fileName
    global curLink
    while True:
        #클라이언트가 'send'버튼으로 text를 전송할 때까지 대기
        data = await websocket.recv();#받는 데이터는 json형태(kinds, text)
        
        json_data = json.loads(data)#받은 데이터를 json으로 변환
        
        #..디렉토리 클릭
        if json_data['kinds']=='chdir' and json_data['text']=='..' and os.getcwd() in available_drives :
            json_dirList = json.dumps({"kinds": "directory", "list": available_drives})
            await websocket.send("{}".format(json_dirList))

        #다른 디렉토리 클릭
        elif json_data['kinds']=='chdir':
            if os.path.isfile(json_data['text']):
                break

            #Linux Version
            #os.chdir(json_data['text']+'/')
            #Linux Version
            #Windows Version
            os.chdir(json_data['text']+'\\')
            #Windows Version
            curLink=json_data['text']+'\\'
            #print(os.getcwd())
            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));


        #파일 및 디렉토리 제거
        elif json_data['kinds']=='remove':
            dirPath=os.getcwd()
            targetName=json_data['text']
            if os.path.isfile(targetName):
                os.remove(targetName)
            elif os.path.isdir(targetName):
                item=os.path.join(dirPath,targetName)
                shutil.rmtree(item)
                
            #update
            os.chdir('..')
            os.chdir(dirPath)
            #Windows Version

            #print(os.getcwd())
            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update

        #이름 변경
        elif json_data['kinds']=='namemodify':
            srcName=json_data['text']
            dstName=json_data['text2']
            os.rename(srcName,dstName)
            #update
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)
            #Windows Version

            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update

        elif json_data['kinds']=='modify':
            fileName=json_data['text']
            f=open(fileName,mode='r+',encoding='utf-8')
            texts=json.dumps({"kinds":"modify","text":f.read()})
            await websocket.send("{}".format(texts));
            f.close()

        elif json_data['kinds']=='modify2':
            fd=os.open(fileName,os.O_CREAT|os.O_RDWR)
            os.write(fd,bytes(json_data['texts'],encoding='utf8'))
            print('{}'.format(json_data['texts']))
            os.close(fd)
            
            #update
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)
            #Windows Version

            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update

        elif json_data['kinds']=='makedir':
            make_dir_name = json_data['text']
            os.mkdir(os.getcwd()+ "\\"+make_dir_name+ "\ ")
            #update
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)
            #Windows Version

            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update
            
        #파일 생성
        elif json_data['kinds'] == 'makename':
            make_file_name = json_data['text']

        elif json_data['kinds'] == 'maketext':
            make_file_text = json_data['text']
            if make_file_name == '':
                print('file name is null')
            else:
                print('make-name:', make_file_name)
                print('make-text:', make_file_text)
                print(os.getcwd())
                fdd=os.open(make_file_name,os.O_CREAT|os.O_RDWR)
                os.write(fdd,bytes(make_file_text,encoding='utf8'))
                os.close(fdd)
                make_file_name=''
                make_file_text=''

            #update
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)
            #Windows Version

            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update

        #파일 복사
        elif json_data['kinds']=='copy':
            targetName=json_data['text']
            targetLink=os.getcwd()
            print(targetLink)
            
        #파일 붙여넣기
        elif json_data['kinds']=='paste':
            print(targetLink, targetName)
            shutil.copy(targetLink+"\\"+targetName,os.getcwd()+ "\\copy_"+targetName)

            #update
            curLink=os.getcwd()
            os.chdir('..')
            os.chdir(curLink)
            #Windows Version

            dirList=['..']
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)

            json_dirList = json.dumps({"kinds": "directory", "list": dirList})
            json_fileList = json.dumps({"kinds": "filelist", "list": fileList})
            await websocket.send("{}".format(json_dirList));
            await websocket.send("{}".format(json_fileList));
            #update
            
def network_info():
    host = socket.gethostname()
    ip_addr = socket.gethostbyname(host)
    print('HOST:' + host)
    print("ip Address:" + ip_addr)
    return ip_addr


ip = network_info()

# 파일 전송용 웹 소켓 서버 생성.호스트는 localhost에 port는 8080으로 생성한다.
start_server = websockets.serve(file_accept, ip, 8080);

# 파일 전송용이 아닌 웹 소켓 서버 생성. 호스트는 localhost에 port는 8081로 생성
start_server_text = websockets.serve(text_accept,  ip, 8081);

# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_until_complete(start_server_text);
asyncio.get_event_loop().run_forever();
