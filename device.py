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
    # the even numbers are "WC" mappings, i believe we want uc=uncached
    if mid%2 == 0: continue
    sz = tmp.out.mappings[i].mapping_size
    print(f"mapping {mid} with size {sz}")
    mappings[mid] = to_mv(libc.mmap(0, sz, mmap.PROT_READ | mmap.PROT_WRITE, mmap.MAP_SHARED,
      fd, tmp.out.mappings[i].mapping_base), sz)
print(f"mapped {len(mappings)}")

sram = mappings[1]
mmio = mappings[3]
vram = mappings[5]

BAR0_BH_SIZE = 512 * 1024 * 1024  # can confirm it's 512MB
ATU_OFFSET_IN_BH_BAR2 = 0x1200

"""
static constexpr auto TLB_2M_OFFSET = tlb_offsets{
    .local_offset = 0,
    .x_end = 43,
    .y_end = 49,
    .x_start = 55,
    .y_start = 61,
    .noc_sel = 67,
    .mcast = 69,
    .ordering = 70,
    .linked = 72,
    .static_vc = 73,
    // missing .stream_header
    .static_vc_end = 75};
"""

def extract_bits(data, start, end):
  width = end - start
  return (data >> start) & ((1 << width) - 1)

STATIC_TLB_CFG_ADDR = 0x1FC00000
tlb_config = sram[STATIC_TLB_CFG_ADDR:STATIC_TLB_CFG_ADDR+0x40000].cast("I")

def dump_tlb_config():
  for i in range(0x10):
    t1,t2,t3 = tlb_config[i*3:i*3+3]
    raw = (t3 << 64) | (t2 << 32) | t1
    #print(i, hex(t1), hex(t2), hex(t3))
    local_offset = extract_bits(raw, 0, 43)
    x_end        = extract_bits(raw, 43, 49)
    y_end        = extract_bits(raw, 49, 55)
    x_start      = extract_bits(raw, 55, 61)
    y_start      = extract_bits(raw, 61, 67)
    noc_sel      = extract_bits(raw, 67, 69)
    mcast        = extract_bits(raw, 69, 70)
    ordering     = extract_bits(raw, 70, 72)
    linked       = extract_bits(raw, 72, 73)
    static_vc    = extract_bits(raw, 73, 75)

    print(f"{i}: local_offset=0x{local_offset:X}, x_end={x_end}, y_end={y_end}, "
          f"x_start={x_start}, y_start={y_start}, noc_sel={noc_sel}, mcast={mcast}, "
          f"ordering={ordering}, linked={linked}, static_vc={static_vc}")

backup0 = tlb_config[0]
backup1 = tlb_config[1]
tlb_config[0] = 0
tlb_config[1] = (1 << (43-32)) | (1 << (49-32))
dump_tlb_config()
hexdump(sram[0:0x40])
print("*****")
tlb_config[0] = backup0
tlb_config[1] = backup1
hexdump(sram[0:0x40])

objdump = "/home/billy/build/tt-metal/build_Release/libexec/tt-metalium/runtime/sfpi/compiler/bin/riscv32-tt-elf-objdump"

f = open("/tmp/dump", "wb")
f.write(sram[0:0x40])
f.close()

os.system(objdump+" -D -b binary -m riscv /tmp/dump")

"""
from capstone import *
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
for i in md.disasm(sram[0:0x100], 0):
  print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
"""


"""
hexdump(vram[0:0x100])

st = b"george waz here"
vram[0:len(st)] = st

hexdump(vram[0:0x100])
"""

