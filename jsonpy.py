import websockets
import os
import glob
import sys
import asyncio
import json
import base64
#기본경로
os.chdir('/')
ndir=nfile=0

##def traverse(dirpath,depth,websocket):
##    global ndir,nfile
##    for obj in glob.glob(dirpath+'/*'):
##        if depth==0:
##            prefix='l--'
##        else:
##            prefix='l'+' '*depth+'l--'
##        print(obj)
##        if os.path.isdir(obj):
##            ndir+=1
##            print(prefix+os.path.basename(obj))
##            websocket.send("{}".format(prefix+os.path.basename(obj)))
##            traverse(obj,depth+1,websocket)
##        elif os.path.isfile(obj):
##            nfile+=1
##            print(prefix+os.path.basename(obj))
##        else:
##            print(prefix+'unknown object :',obj)

# 클라이언트 접속이 되면 호출된다.
async def accept(websocket, path): #코루틴함수 
    dirList=[]
    fileList=[]
    #file_list=os.listdir(os.getcwd())
    for i in os.listdir():
        if os.path.isfile(i):
            fileList.append(i)
        else:
            dirList.append(i)
    await websocket.send("{}{}".format('directory = ',dirList))
    await websocket.send("{}{}".format('file = ',fileList))
    
    while True:
    # 클라이언트로부터 메시지를 대기한다.
        tmp = await websocket.recv(); #명령어
        tmp = json.loads(tmp)   #tmp는 json데이터
        msgType=tmp["type"]     #msgType은 tmp의 type
        msgText=tmp["text"]     #msgText는 tmp의 text
        
        if msgType=="exit":     #disconnect
            sys.exit(1)
            
        if msgType=="fileName":
            fileName=msgText.split()[1]
            print("fileName = ",fileName)

        elif msgType=="mkdir":      #디렉토리 생성
            dirName=msgText
            print("dirName = ",dirName)
            os.mkdir(os.getcwd()+ "\\"+dirName+ "\ ")
            
        elif msgType=="rmdir":
            try:
                dirName=msgText
                print("dirName = ",dirName)
                os.rmdir(dirName)
            except OSError as error:
                print(error)
                await websocket.send("{}{}".format(error,"디렉토리를 비워주세요"))

        elif msgType=="remove":
            fileName=msgText
            print("fileName = ",fileName)
            os.remove(fileName)
                
        elif msgType=="message2":   #submit 눌렀을때
            fd=os.open(fileName,os.O_CREAT|os.O_RDWR)
            os.write(fd,bytes(msgText,encoding='utf8'))
            print('{}'.format(msgText))
            
        elif msgType=="message1":   #디렉토리명을 입력 받았을때
            os.chdir(msgText)
            dirList=[]
            fileList=[]
            for i in os.listdir():
                if os.path.isfile(i):
                    fileList.append(i)
                else:
                    dirList.append(i)
            # 클라이언트가 확인할 수 있게 웹소켓에 결과값을 출력 
            await websocket.send("{}{}".format('directory = ',dirList))
            await websocket.send("{}{}".format('file = ',fileList))
            

if __name__=="__main__":
    # 웹 소켓 서버 생성.호스트는 localhost에 port는 9998로 생성한다.
    start_server = websockets.serve(accept, "192.168.0.51", 9998);
    # 비동기로 서버를 대기한다.
    asyncio.get_event_loop().run_until_complete(start_server);
    asyncio.get_event_loop().run_forever();


