import asyncio
import os
import aiopg
import sys
from email.message import EmailMessage
import aiosmtplib

db=os.environ.get('EDATABASE')
user=os.environ.get('EUSER')
psw=os.environ.get('EPASSWORD')
host=os.environ.get('EHOST')

#передаем секретные данные через переменные окружения
dsn = f'dbname={db} user={user} password={psw} host={host}'

EMAIL_BODY=r"Уважаемый, name! Спасибо, что пользуетесь нашим сервисом объявлений."
FROM="vyacheslav.beketov@gmail.com"
SUBJECT="Благодарим за сотрудничество"

#  подпрограмма (coroutine) верхнего уровня
async def main():
    #Подключаемся к БД и получаем список пользователей
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM public.user")
                ret = []
                async for row in cur:
                    ret.append(row)
                    #print(row)

            async with aiosmtplib.SMTP(
                    hostname='smtp.gmail.com', #'smtp.yandex.ru'
                    port=587, #465 (Yandex), 587 (Google)
                    username='vyacheslav.beketov@gmail.com', #'netology-test-user@yandex.ru',
                    password=os.environ.get('SPASSWORD'),
                    start_tls=True) as smtp:
                #по всем адресатам
                for adress in ret:
                    #если пользователь не указал e-mail - пропускаем
                    if adress[2] == None:
                        continue
                    #чтобы избежать текста сообщения в ascii
                    body=EMAIL_BODY.replace('name',adress[1]).encode('utf-8')
                    await smtp.sendmail(FROM, adress[2], body)

    return ret

if __name__ == '__main__':
    #Снова Windows козни строит)): https://github.com/aio-libs/aiopg/issues/678
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    #event loop (цикл обработки событий) управляет планированием и передачей awaitable объектов
    loop = asyncio.get_event_loop()
    # точка входа в программу asyncio
    loop.run_until_complete(main())

