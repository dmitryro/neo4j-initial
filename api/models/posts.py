# Copyright 2016 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import url_for


class Post(object):
    __data = []
    __index = 0

    def __init__(self, id = 0, name='', category=''):
        self.id = id
        self.name = name
        self.category = category

    def save(self):
        if self.id == 0:
            self.id = self.__next_index()
            Post.__data.append(self)
        else:
            for i in range(len(Post.__data)):
                if Post.__data[i].id == self.id:
                    Post.__data[i] = self
                    break

    def delete(self):
        Post.__data.remove(self)

    def __next_index(self):
        Post.__index += 1
        return Post.__index

    def serialize(self):
        return { "id": self.id, "name": self.name, "category": self.category }

    def self_url(self):
        return url_for('get_posts', id=self.id, _external=True)

    def deserialize(self, data):
        if not isinstance(data, dict):
            raise ValueError('Invalid post: body of request contained bad or no data')
        if data.has_key('id'):
            self.id = data['id']
        try:
            self.name = data['name']
            self.category = data['category']
        except KeyError as e:
            raise ValueError('Invalid post: missing ' + e.args[0])
        return

    @staticmethod
    def all():
        return [post for post in Post.__data]

    @staticmethod
    def remove_all():
        del Post.__data[:]
        Post.__index = 0
        return Post.__data

    @staticmethod
    def find(id):
        if len(Post.__data) == 0:
            return None
        posts = [post for post in Post.__data if post.id == id]
        if len(posts) > 0:
            return posts[0]
        return None

    @staticmethod
    def find_by_category(category):
        return [post for post in Post.__data if post.category == category]

    @staticmethod
    def find_by_name(name):
        return [post for post in Post.__data if post.name == name]
