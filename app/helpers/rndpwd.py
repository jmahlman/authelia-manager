#    This code is a portion of frigate Event Video Recorder (fEVR)
#
#    Copyright (C) 2021-2022  The Bearded Tek (http://www.beardedtek.com) William Kenny
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU AfferoGeneral Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import secrets
import string

class randpwd:
    def generate(count=None,key=False):
        if key == True:
            count = 128
        else:
            count = secrets.randbelow(40) + 24
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(count))
        return password

if __name__ == '__main__':
    print(randpwd.generate(key=True))
    print()
    print(randpwd.generate(count=63))
