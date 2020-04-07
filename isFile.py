import websockets
import os
import sys
import asyncio
#기본경로
os.chdir('/')

# 클라이언트 접속이 되면 호출된다.
async def accept(websocket, path):
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
        msg = await websocket.recv();
        if msg=="exit":
            sys.exit(1)
        os.chdir(msg);
    # 클라이언트로 echo를 붙여서 재 전송한다.
        dirList=[]
        fileList=[]
        for i in os.listdir():
            if os.path.isfile(i):
                fileList.append(i)
            else:
                dirList.append(i)
        await websocket.send("{}{}".format('directory = ',dirList))
        await websocket.send("{}{}".format('file = ',fileList))
        #await websocket.send("{}".format(file_list));

# 웹 소켓 서버 생성.호스트는 localhost에 port는 9998로 생성한다.
start_server = websockets.serve(accept, "172.30.6.46", 9997);
# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(start_server);
asyncio.get_event_loop().run_forever();


