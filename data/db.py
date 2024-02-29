import psycopg2
import datetime
from psycopg2.extras import DictCursor
import utils

db_uri = "POSTGRESQL DATABASE CONNECTION"

class SQLighter:
    def __init__(self, db_uri):
        self.connection = psycopg2.connect(db_uri)
        self.cursor = self.connection.cursor()
        
    def create_user(self, username, password_hash, email):
        # Добавление нового пользователя в базу данных
        self.cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)', (username, password_hash, email))
        self.connection.commit()

    def get_user(self, username):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            return cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
    
    def get_posts(self):
        self.cursor.execute('''
            SELECT posts.id, posts.text, posts.image_url, posts.created_at, users.username, posts.head_title, posts.username, posts.post_owner_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        ''')
        return self.cursor.fetchall()
    
    def get_posts_by_id(self, user_id):
        self.cursor.execute('''
            SELECT posts.id, posts.text, posts.image_url, posts.created_at, users.username, posts.head_title, posts.username, posts.post_owner_id
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.post_owner_id = '%s'
            ORDER BY posts.created_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()

        
    def update_last_seen(self, username):
        current_time = datetime.datetime.now()
        self.cursor.execute('UPDATE users SET last_seen = %s WHERE username = %s', (current_time, username))
        self.connection.commit()

    def get_last_seen(self, username):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT last_seen FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
            return result['last_seen']


    def get_user_by_id(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()


    def is_online(self, last_seen):
        if last_seen:
            utc_time = datetime.datetime.utcnow()
            moscow_time = utc_time + datetime.timedelta(hours=3)  # Сдвиг на 3 часа вперед от UTC
            return (moscow_time - last_seen) < datetime.timedelta(minutes=1)
        return False
    
    def update_avatar(self, file, user_id):
        filename = f'avatar_{user_id}_{file.filename}'
        utils.upload_to_s3v2(self, file=file, filename=filename)
        self.cursor.execute('UPDATE users SET img_avatar = %s WHERE id = %s', (filename, user_id))
        self.connection.commit()

    def get_avatar(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT img_avatar FROM users WHERE id = %s', (user_id,))
            result = cursor.fetchone()
            if result and result['img_avatar']:
                avatar_name = result['img_avatar']
                return utils.find_s3(avatar_name)
            else:
                return None  # Или URL изображения по умолчанию, если аватар отсутствует
        
    def create_post(self, text, image_url, head_title, username, post_owner_id):
        query = '''
        INSERT INTO posts (text, user_id, image_url, created_at, head_title, username, post_owner_id) 
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)

        '''
        try:
            self.cursor.execute(query, (text, 3, image_url, head_title, username, post_owner_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при создании поста: {e}")
            self.connection.rollback()
            return False
        
    def update_friend(self, sender_id, to_user_id, status):
        if status == 'send':
            self.cursor.execute('INSERT INTO friends (user_id1, user_id2, status) VALUES (%s, %s, %s)', (sender_id, to_user_id, 'pending'))
            self.connection.commit()
        elif status == 'accepted':
            self.cursor.execute('UPDATE friends SET status = %s WHERE id = %s', ('accepted', sender_id))
            self.connection.commit() 

    def get_friend_requests(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = """
            SELECT u.id as user_id, u.username as sender_username, f.id as request_id
            FROM friends f
            JOIN users u ON f.user_id1 = u.id
            WHERE f.user_id2 = %s AND f.status = 'pending'
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        
    def get_friends(self, user_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            # This query fetches the user IDs of friends.
            query = """
            SELECT f.user_id1, f.user_id2
            FROM friends f
            WHERE (f.user_id1 = %s OR f.user_id2 = %s) AND f.status = 'accepted'
            """
            cursor.execute(query, (user_id, user_id))
            rows = cursor.fetchall()
        
        # Now fetch the usernames using the get_user_by_id function
        friend_usernames = []
        for row in rows:
            # Check which user_id is the friend's ID and get their username
            friend_id = row['user_id1'] if row['user_id2'] == user_id else row['user_id2']
            friend_info = self.get_user_by_id(friend_id)
            if friend_info:
                friend_usernames.append(friend_info['username'])
        print(friend_usernames)
        return friend_usernames
    
    def add_comment(self, post_id, text, user_id):
        if post_id:
            self.cursor.execute('INSERT INTO comments (post_id, text, user_id) VALUES (%s, %s, %s)', (post_id, text, user_id))
            self.connection.commit()

    def get_comments(self, post_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = """
            SELECT c.id, c.text, c.created_at, u.username, u.id as user_id
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
            """
            cursor.execute(query, (post_id,))
            return cursor.fetchall()

    def get_conversations(self, user_id):
        # Получение списка переписок для пользователя
        query = """
        SELECT conversation_id, participant_one, participant_two
        FROM conversations
        WHERE participant_one = %s OR participant_two = %s;
        """
        self.cursor.execute(query, (user_id, user_id))
        return self.cursor.fetchall()
    
    def is_user_part_of_conversation(self, user_id, conversation_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1
                FROM conversations
                WHERE (participant_one = %s OR participant_two = %s)
                AND conversation_id = %s
            """, (user_id, user_id, conversation_id))
            return cursor.fetchone() is not None

    def get_messages(self, conversation_id):
        # Получение сообщений в переписке
        query = """
        SELECT message_id, sender_id, message_text, timestamp, is_read
        FROM messages
        WHERE conversation_id = %s;
        """
        self.cursor.execute(query, (conversation_id,))
        return self.cursor.fetchall()

    def send_message(self, conversation_id, sender_id, message_text):
        # Отправка нового сообщения
        query = """
        INSERT INTO messages (conversation_id, sender_id, message_text)
        VALUES (%s, %s, %s);
        """
        self.cursor.execute(query, (conversation_id, sender_id, message_text))
        self.connection.commit()

    def mark_message_as_read(self, message_id):
        # Обновление статуса сообщения как прочитанное
        query = """
        UPDATE messages
        SET is_read = TRUE
        WHERE message_id = %s;
        """
        self.cursor.execute(query, (message_id,))
        self.connection.commit()

    def get_conversation_id(self, user_id1, user_id2):
        # Возвращает ID беседы между двумя пользователями
        query = """
        SELECT conversation_id
        FROM conversations
        WHERE (participant_one = %s AND participant_two = %s) OR (participant_one = %s AND participant_two = %s);
        """
        self.cursor.execute(query, (user_id1, user_id2, user_id2, user_id1))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def create_conversation(self, user_id1, user_id2):
        # Создаем новую запись в таблице `conversations`
        query = """
        INSERT INTO conversations (participant_one, participant_two)
        VALUES (%s, %s) RETURNING conversation_id;
        """
        try:
            self.cursor.execute(query, (user_id1, user_id2))
            conversation_id = self.cursor.fetchone()[0]  # Получаем ID новой беседы
            self.connection.commit()
            return conversation_id
        except Exception as e:
            print(f"Ошибка при создании беседы: {e}")
            self.connection.rollback()
            return None
