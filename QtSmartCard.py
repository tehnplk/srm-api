from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import HexListToBinString, toHexString, toBytes
import time
from PyQt6.QtCore import QThread, pyqtSignal


class SmartCardObserver(CardObserver, QThread):
    signal_state = pyqtSignal(dict)
    signal_data = pyqtSignal(dict)
    signal_photo = pyqtSignal(dict)
    _CMD_RESET = [0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]

    def __init__(self, read_photo):
        QThread.__init__(self)
        CardMonitor().addObserver(self)
        self.read_photo = read_photo
        self._birth_en = None

    def stop(self):
        CardMonitor().deleteObserver(self)

    def th_unicode(self, data):
        result = bytes(data).decode('tis-620')
        return result.strip()

    def get_card_data(self, con, req, cmd):
        con.transmit(cmd)
        data, sw1, sw2 = con.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]

    def getData(self, con, req, cmd):
        con.transmit(cmd)
        data, sw1, sw2 = con.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]

    def update(self, observable, actions):
        (added_card, removed_card) = actions
        print('smc_action', actions)

        if added_card:
            self.signal_state.emit({
                'state': 'inserted'
            })
            card = added_card[0]
            try:
                con = card.createConnection()
                con.connect()
                atr = con.getATR()
                if atr[0] == 0x3B & atr[1] == 0x67:
                    req = [0x00, 0xc0, 0x00, 0x01]
                else:
                    req = [0x00, 0xc0, 0x00, 0x00]

                con.transmit(self._CMD_RESET)

                time.sleep(0.5)

                _CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_CID)
                _cid = self.th_unicode(data)

                _CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_THFULLNAME)
                _thfullname = self.th_unicode(data)

                _CMD_ENFULLNAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_ENFULLNAME)
                _enfullname = self.th_unicode(data)

                _CMD_BIRTH = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_BIRTH)
                _birth = self.th_unicode(data)

                _CMD_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_GENDER)
                _gender = self.th_unicode(data)

                _CMD_ADDR = [0x80, 0xB0, 0x15, 0x79, 0x02, 0x00, 0x64]
                data, sw1, sw2 = self.get_card_data(con, req, _CMD_ADDR)
                _addr = self.th_unicode(data)

                try:
                    yyyy, mm, dd = int(_birth[:-4]) - 543, _birth[4:-2], _birth[6:]
                    self._birth_en = f"{yyyy}-{mm}-{dd}"
                except:
                    self._birth_en = None

                self.signal_data.emit({
                    'cid': _cid,
                    'thfullname': _thfullname,
                    'enfullname': _enfullname,
                    'birth': _birth,
                    'birth_en': self._birth_en,
                    'gender': _gender,
                    'addr': _addr

                })

            except Exception as e:
                print('err', e)
                self.signal_data.emit({
                    'cid': 'err',
                    'thfullname': 'read smc error.',
                    'enfullname': 'read smc error.',
                    'birth': None,
                    'birth_en': None,
                    'gender': None
                })

            try:
                """ CMD PHOTO """
                # Photo_Part1/20
                CMD_PHOTO1 = [0x80, 0xb0, 0x01, 0x7B, 0x02, 0x00, 0xFF]
                # Photo_Part2/20
                CMD_PHOTO2 = [0x80, 0xb0, 0x02, 0x7A, 0x02, 0x00, 0xFF]
                # Photo_Part3/20
                CMD_PHOTO3 = [0x80, 0xb0, 0x03, 0x79, 0x02, 0x00, 0xFF]
                # Photo_Part4/20
                CMD_PHOTO4 = [0x80, 0xb0, 0x04, 0x78, 0x02, 0x00, 0xFF]
                # Photo_Part5/20
                CMD_PHOTO5 = [0x80, 0xb0, 0x05, 0x77, 0x02, 0x00, 0xFF]
                # Photo_Part6/20
                CMD_PHOTO6 = [0x80, 0xb0, 0x06, 0x76, 0x02, 0x00, 0xFF]
                # Photo_Part7/20
                CMD_PHOTO7 = [0x80, 0xb0, 0x07, 0x75, 0x02, 0x00, 0xFF]
                # Photo_Part8/20
                CMD_PHOTO8 = [0x80, 0xb0, 0x08, 0x74, 0x02, 0x00, 0xFF]
                # Photo_Part9/20
                CMD_PHOTO9 = [0x80, 0xb0, 0x09, 0x73, 0x02, 0x00, 0xFF]
                # Photo_Part10/20
                CMD_PHOTO10 = [0x80, 0xb0, 0x0A, 0x72, 0x02, 0x00, 0xFF]
                # Photo_Part11/20
                CMD_PHOTO11 = [0x80, 0xb0, 0x0B, 0x71, 0x02, 0x00, 0xFF]
                # Photo_Part12/20
                CMD_PHOTO12 = [0x80, 0xb0, 0x0C, 0x70, 0x02, 0x00, 0xFF]
                # Photo_Part13/20
                CMD_PHOTO13 = [0x80, 0xb0, 0x0D, 0x6F, 0x02, 0x00, 0xFF]
                # Photo_Part14/20
                CMD_PHOTO14 = [0x80, 0xb0, 0x0E, 0x6E, 0x02, 0x00, 0xFF]
                # Photo_Part15/20
                CMD_PHOTO15 = [0x80, 0xb0, 0x0F, 0x6D, 0x02, 0x00, 0xFF]
                # Photo_Part16/20
                CMD_PHOTO16 = [0x80, 0xb0, 0x10, 0x6C, 0x02, 0x00, 0xFF]
                # Photo_Part17/20
                CMD_PHOTO17 = [0x80, 0xb0, 0x11, 0x6B, 0x02, 0x00, 0xFF]
                # Photo_Part18/20
                CMD_PHOTO18 = [0x80, 0xb0, 0x12, 0x6A, 0x02, 0x00, 0xFF]
                # Photo_Part19/20
                CMD_PHOTO19 = [0x80, 0xb0, 0x13, 0x69, 0x02, 0x00, 0xFF]
                # Photo_Part20/20
                CMD_PHOTO20 = [0x80, 0xb0, 0x14, 0x68, 0x02, 0x00, 0xFF]

                # READ PHOTO
                if self.read_photo:
                    photo = self.get_card_data(con, req, CMD_PHOTO1)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO2)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO3)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO4)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO5)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO6)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO7)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO8)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO9)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO10)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO11)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO12)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO13)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO14)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO15)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO16)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO17)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO18)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO19)[0]
                    photo += self.get_card_data(con, req, CMD_PHOTO20)[0]
                    img = bytes(photo)
                else:
                    img = None
                """ END READ PHOTO"""

                self.signal_photo.emit({
                    'cid': _cid,
                    'img': img
                })

            except Exception as e:
                self.signal_photo.emit({
                    'img': 'err'
                })

            con.transmit(self._CMD_RESET)
            self.signal_state.emit({
                'state': 'read'
            })

        if removed_card:
            self.signal_state.emit({
                'state': 'removed',

            })
