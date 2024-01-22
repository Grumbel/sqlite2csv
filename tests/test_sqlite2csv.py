# sqlite2csv - Convert .sqlite3 database files to .csv
# Copyright (C) 2024 Ingo Ruhnke <grumbel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest

import sqlite3
from io import StringIO

from typing import TextIO

import sqlite2csv


class Sqlite2CsvTestCase(unittest.TestCase):

    def test_sqlite2csv(self) -> None:
        io_dict: dict[str, StringIO] = {}

        def io_from_tablename(tablename: str) -> TextIO:
            string_io = StringIO()

            # StringIO.getvalue() can't be accessed after close, thus disable close
            string_io.close = lambda: None  # type: ignore

            io_dict[tablename] = string_io
            return string_io

        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE MyTable ( " +
                         "id INTEGER PRIMARY KEY, " +
                         "name TEXT NOT NULL, " +
                         "title TEXT NOT NULL, " +
                         "number INTEGER NOT NULL " +
                         ")")
            conn.execute("INSERT into MyTable(name, title, number) VALUES " +
                         "('name1', 'title1', 100), " +
                         "('name2', 'title2', 200), " +
                         "('name3', 'title3', 300)"
                         )
            conn.execute("CREATE TABLE MyTable2 ( " +
                         "id INTEGER PRIMARY KEY, " +
                         "name TEXT NOT NULL, " +
                         "title TEXT NOT NULL " +
                         ")")
            conn.execute("INSERT into MyTable2(name, title) VALUES " +
                         "('name1, lastname1', 'title1 title1'), " +
                         "('name2 lastname2', 'title2,title2'), " +
                         "('name3, lastname3', 'title3 title3')"
                         )

            sqlite2csv.sqlite2csv(conn, io_from_tablename)

            results = [(k, v.getvalue()) for k, v in io_dict.items()]

            expected = \
                [('MyTable',
                  'id,name,title,number\r\n'
                  '1,name1,title1,100\r\n'
                  '2,name2,title2,200\r\n'
                  '3,name3,title3,300\r\n'),
                 ('MyTable2',
                  'id,name,title\r\n'
                  '1,"name1, lastname1",title1 title1\r\n'
                  '2,name2 lastname2,"title2,title2"\r\n'
                  '3,"name3, lastname3",title3 title3\r\n'),
                 ]

            self.assertEqual(expected, results)


# EOF #
