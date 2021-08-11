import sys
from sys import platform
from collections import deque
from modbus_crc16 import crc16


if platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()


class CheckCRC:
    def __init__(self, firmware, lo_byte):
        array = ('@', ';', '#', 'q')

        self.firmware = firmware
        self.dump = deque()

        with open(self.firmware) as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith(array):
                continue
            tmp = [int(x, 16) for x in line.rstrip().split()]
            self.dump.extend(tmp)

        self.hi_byte = -1
        self.lo_byte = lo_byte
        self.__CRC_PO = '7E F5'
        self._CHK_CRC = crc16(self.dump)
        self.checked_crc()

    def checked_crc(self):
        bad_crc = self._CHK_CRC
        checked = [self.lo_byte, self.hi_byte]
        flag = True
        while self._CHK_CRC != self.__CRC_PO:
            flag = False
            if self.hi_byte != 255:
                self.hi_byte += 1
            else:
                self.hi_byte = 0
                if self.lo_byte != 255:
                    self.lo_byte += 1
                else:
                    print(f"{c.FAIL}Не удалось определить значение.{c.END}")
                    sys.exit()
            checked[-2], checked[-1] = self.lo_byte, self.hi_byte
            self._CHK_CRC = crc16(checked, int(bad_crc[:2], 16), int(bad_crc[2:], 16))

            sys.stdout.write(f"Пробуем значение - "
                             f"{c.BLUE}{format(self.lo_byte, '02X')} "
                             f"{format(self.hi_byte, '02X')}{c.END}\r")
            sys.stdout.flush()
        if flag:
            print(f"Перебор не требуется.\n"
                  f"CRC ПО - {c.FAIL}{self._CHK_CRC}{c.END}\n"
                  f"Контрольные байты - "
                  f"{c.FAIL}{format(self.dump[-2], '02X')} {format(self.dump[-1], '02X')}{c.END}")
        else:
            print(f"Контрольные байты - "
                  f"{c.FAIL}{format(self.lo_byte, '02X')} {format(self.hi_byte, '02X')}{c.END}\n"
                  f"CRC ПО - {c.FAIL}{self._CHK_CRC}.{c.END}")


if __name__ == '__main__':
    file_CRC_PO = 'CRC_PO_2021.txt'
    file_CRC_UPDATE = 'CRC_UPDATE_2021.txt'

    CheckCRC(file_CRC_UPDATE, lo_byte=0x00)
