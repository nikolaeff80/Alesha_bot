import os

from openai import OpenAI
from time import sleep
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
client = OpenAI(api_key=API_KEY)
starting_assistant = ""
starting_thread = ""


def create_assistant():
    if starting_assistant == "":
        my_assistant = client.beta.assistants.create(
            instructions="Ты робот Алеша. Продавец сноубордов. Даешь рекомендации по подбору доски для сноуборда."
                         "Можешь у пользователя спрашивать дополнительную информацию, такую как: "
                         "Имя, Опыт, Цель, Стиль и любую другую полезную информацию.",
            name="Robot Alesha",
            model="gpt-3.5-turbo",
        )
    else:
        my_assistant = client.beta.assistants.retrieve(starting_assistant)

    return my_assistant


def create_thread():
    if starting_thread == "":
        thread = client.beta.threads.create()
    else:
        thread = client.beta.threads.retrieve(starting_thread)

    return thread


def send_message(thread_id, message):
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message,
    )
    return thread_message


def run_assistant(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )
    return run


def get_newest_message(thread_id):
    thread_messages = client.beta.threads.messages.list(thread_id)
    return thread_messages.data[0]


def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status


def main():
    my_assistant = create_assistant()
    my_thread = create_thread()
    print("Привет! Я робот Алеша! И я помогу тебе выбрать сноуборд")
    
    while True:
        user_message = input("Введите ваше сообщение: ")
        if user_message.lower() == "exit":
            break

        send_message(my_thread.id, user_message)
        run = run_assistant(my_thread.id, my_assistant.id)
        while run.status != "completed":
            run.status = get_run_status(my_thread.id, run.id)
            sleep(1)
            print("⏳", end="\r", flush=True)

        sleep(0.5)
        response = get_newest_message(my_thread.id)
        print("Robot Alesha:", response.content[0].text.value)


if __name__ == "__main__":
    main()
    