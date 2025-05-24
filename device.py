import os, fcntl, mmap
from hexdump import hexdump
import autogen.tt_ioctl as tt_ioctl
from tinygrad.runtime.autogen import libc
from tinygrad.helpers import to_mv
fd = os.open("/dev/tenstorrent/0", os.O_RDWR)

tmp = tt_ioctl.struct_tenstorrent_query_mappings()
getattr(tmp, 'in').output_mapping_count = 16
ret = fcntl.ioctl(fd, (tt_ioctl.TENSTORRENT_IOCTL_MAGIC<<8) | 2, tmp)
assert ret == 0

mappings = {}
for i in range(16):
  if (mid:=tmp.out.mappings[i].mapping_id) != 0:
    if mid%2 == 0: continue
    sz = tmp.out.mappings[i].mapping_size
    print(f"mapping {mid} with size {sz}")
    mappings[mid] = to_mv(libc.mmap(0, sz, mmap.PROT_READ | mmap.PROT_WRITE, mmap.MAP_SHARED,
      fd, tmp.out.mappings[i].mapping_base), sz)
print(f"mapped {len(mappings)}")

sram = mappings[1]
mmio = mappings[3]
vram = mappings[5]

hexdump(mmio[0:0x100])

"""
hexdump(vram[0:0x100])

st = b"george waz here"
vram[0:len(st)] = st

hexdump(vram[0:0x100])
"""


