import hashlib

SCOPEID = '0000000000000000'
Model   = 'SDS2000X+'

# Note that 'AWG' should be used for the 'FG' option
# If you have the 100 MHz model, then first upgrade it to 200 MHz, then 350 MHz and finally 500 MHz
bwopt = ('25M', '40M', '50M', '60M', '70M', '100M', '150M', '200M', '250M', '300M', '350M', '500M', '750M', '1000M', 'MAX', 'AWG', 'WIFI', 'MSO', 'FLX', 'CFD', 'I2S', '1553', 'PWA')

hashkey = '5zao9lyua01pp7hjzm3orcq90mds63z6zi5kv7vmv3ih981vlwn06txnjdtas3u2wa8msx61i12ueh14t7kqwsfskg032nhyuy1d9vv2wm925rd18kih9xhkyilobbgy'

def gen(x):
    h = hashlib.md5((
        hashkey +
        (Model+'\n').ljust(32, '\x00') +
        x.ljust(5, '\x00') +
        2*((SCOPEID + '\n').ljust(32, '\x00')) +
        '\x00'*16).encode('ascii')
    ).digest()
    key = ''
    for b in h:
        if (b <= 0x2F or b > 0x39) and (b <= 0x60 or b > 0x7A):
            m = b % 0x24
            b = m + (0x57 if m > 9 else 0x30)
        if b == 0x30: b = 0x32
        if b == 0x31: b = 0x33
        if b == 0x6c: b = 0x6d
        if b == 0x6f: b = 0x70
        key += chr(b)
    return key.upper()

for opt in bwopt:
    n = 4
    line = gen(opt)
    print('{:5} {}'.format(opt, [line[i:i+n] for i in range(0, len(line), n)]))
