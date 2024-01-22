#!/usr/bin/env python

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


import argparse
import csv
import sys

import sqlite3

from typing import TextIO, Callable


def csv_io_from_tablename(basepath: str, tablename: str) -> TextIO:
    filename = f"{basepath}{tablename}.csv"
    return open(filename, "w", newline='', encoding='utf-8')


def sqlite2csv(conn: sqlite3.Connection, io_from_tablename: Callable[[str], TextIO]) -> None:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [x for (x,) in cursor.fetchall()]

    for table_name in table_names:
        with io_from_tablename(table_name) as fout:
            io_name = fout.name if hasattr(fout, 'name') else type(fout).__name__
            print(f"Writing {io_name}")

            # Get header names
            cursor.execute(f"SELECT * from {table_name};")
            column_names = [x[0] for x in cursor.description]

            csv_writer = csv.DictWriter(fout, fieldnames=column_names)
            csv_writer.writeheader()

            # Get table data
            cursor.execute(f"SELECT * from {table_name};")
            for row in cursor.fetchall():
                csv_writer.writerow(dict(zip(column_names, row)))


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Convert sqlite to csv')
    parser.add_argument('DATABASE',
                        help='Path to the SQLite database file')
    parser.add_argument('-o', '--output-base', required=True,
                        help='Basename for the .csv output')
    results = parser.parse_args(args)
    return results


def main(argv: list[str]) -> None:
    opts = parse_args(argv[1:])

    with sqlite3.connect(opts.DATABASE) as conn:
        sqlite2csv(conn, lambda tablename: csv_io_from_tablename(opts.output_base, tablename))


def main_entrypoint() -> None:
    main(sys.argv)


if __name__ == "__main__":
    main_entrypoint()


# EOF #
