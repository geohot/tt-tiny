# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes



import fcntl, functools

def _do_ioctl(__idir, __base, __nr, __user_struct, __fd, **kwargs):
  ret = fcntl.ioctl(__fd, (__idir<<30) | (ctypes.sizeof(made := __user_struct(**kwargs))<<16) | (__base<<8) | __nr, made)
  if ret != 0: raise RuntimeError(f"ioctl returned {ret}")
  return made

def _IO(base, nr): return functools.partial(_do_ioctl, 0, ord(base) if isinstance(base, str) else base, nr, None)
def _IOW(base, nr, type): return functools.partial(_do_ioctl, 1, ord(base) if isinstance(base, str) else base, nr, type)
def _IOR(base, nr, type): return functools.partial(_do_ioctl, 2, ord(base) if isinstance(base, str) else base, nr, type)
def _IOWR(base, nr, type): return functools.partial(_do_ioctl, 3, ord(base) if isinstance(base, str) else base, nr, type)

class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass





TTDRIVER_IOCTL_H_INCLUDED = True # macro
TENSTORRENT_DRIVER_VERSION = 2 # macro
TENSTORRENT_IOCTL_MAGIC = 0xFA # macro
TENSTORRENT_IOCTL_GET_DEVICE_INFO = _IO ( 0xFA , 0 ) # macro (from list)
TENSTORRENT_IOCTL_GET_HARVESTING = _IO ( 0xFA , 1 ) # macro (from list)
TENSTORRENT_IOCTL_QUERY_MAPPINGS = _IO ( 0xFA , 2 ) # macro (from list)
TENSTORRENT_IOCTL_ALLOCATE_DMA_BUF = _IO ( 0xFA , 3 ) # macro (from list)
TENSTORRENT_IOCTL_FREE_DMA_BUF = _IO ( 0xFA , 4 ) # macro (from list)
TENSTORRENT_IOCTL_GET_DRIVER_INFO = _IO ( 0xFA , 5 ) # macro (from list)
TENSTORRENT_IOCTL_RESET_DEVICE = _IO ( 0xFA , 6 ) # macro (from list)
TENSTORRENT_IOCTL_PIN_PAGES = _IO ( 0xFA , 7 ) # macro (from list)
TENSTORRENT_IOCTL_LOCK_CTL = _IO ( 0xFA , 8 ) # macro (from list)
TENSTORRENT_IOCTL_MAP_PEER_BAR = _IO ( 0xFA , 9 ) # macro (from list)
TENSTORRENT_IOCTL_UNPIN_PAGES = _IO ( 0xFA , 10 ) # macro (from list)
TENSTORRENT_IOCTL_ALLOCATE_TLB = _IO ( 0xFA , 11 ) # macro (from list)
TENSTORRENT_IOCTL_FREE_TLB = _IO ( 0xFA , 12 ) # macro (from list)
TENSTORRENT_IOCTL_CONFIGURE_TLB = _IO ( 0xFA , 13 ) # macro (from list)
TENSTORRENT_MAPPING_UNUSED = 0 # macro
TENSTORRENT_MAPPING_RESOURCE0_UC = 1 # macro
TENSTORRENT_MAPPING_RESOURCE0_WC = 2 # macro
TENSTORRENT_MAPPING_RESOURCE1_UC = 3 # macro
TENSTORRENT_MAPPING_RESOURCE1_WC = 4 # macro
TENSTORRENT_MAPPING_RESOURCE2_UC = 5 # macro
TENSTORRENT_MAPPING_RESOURCE2_WC = 6 # macro
TENSTORRENT_MAX_DMA_BUFS = 256 # macro
TENSTORRENT_MAX_INBOUND_TLBS = 256 # macro
TENSTORRENT_RESOURCE_LOCK_COUNT = 64 # macro
TENSTORRENT_RESET_DEVICE_RESTORE_STATE = 0 # macro
TENSTORRENT_RESET_DEVICE_RESET_PCIE_LINK = 1 # macro
TENSTORRENT_RESET_DEVICE_CONFIG_WRITE = 2 # macro
TENSTORRENT_PIN_PAGES_CONTIGUOUS = 1 # macro
TENSTORRENT_PIN_PAGES_NOC_DMA = 2 # macro
TENSTORRENT_PIN_PAGES_NOC_TOP_DOWN = 4 # macro
TENSTORRENT_LOCK_CTL_ACQUIRE = 0 # macro
TENSTORRENT_LOCK_CTL_RELEASE = 1 # macro
TENSTORRENT_LOCK_CTL_TEST = 2 # macro
class struct_tenstorrent_get_device_info_in(Structure):
    pass

struct_tenstorrent_get_device_info_in._pack_ = 1 # source:False
struct_tenstorrent_get_device_info_in._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
]

class struct_tenstorrent_get_device_info_out(Structure):
    pass

struct_tenstorrent_get_device_info_out._pack_ = 1 # source:False
struct_tenstorrent_get_device_info_out._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('vendor_id', ctypes.c_uint16),
    ('device_id', ctypes.c_uint16),
    ('subsystem_vendor_id', ctypes.c_uint16),
    ('subsystem_id', ctypes.c_uint16),
    ('bus_dev_fn', ctypes.c_uint16),
    ('max_dma_buf_size_log2', ctypes.c_uint16),
    ('pci_domain', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 2),
]

class struct_tenstorrent_get_device_info(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_get_device_info_in),
    ('out', struct_tenstorrent_get_device_info_out),
     ]

class struct_tenstorrent_query_mappings_in(Structure):
    pass

struct_tenstorrent_query_mappings_in._pack_ = 1 # source:False
struct_tenstorrent_query_mappings_in._fields_ = [
    ('output_mapping_count', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32),
]

class struct_tenstorrent_mapping(Structure):
    pass

struct_tenstorrent_mapping._pack_ = 1 # source:False
struct_tenstorrent_mapping._fields_ = [
    ('mapping_id', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32),
    ('mapping_base', ctypes.c_uint64),
    ('mapping_size', ctypes.c_uint64),
]

class struct_tenstorrent_query_mappings_out(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('mappings', struct_tenstorrent_mapping * 16),
     ]

class struct_tenstorrent_query_mappings(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_query_mappings_in),
    ('out', struct_tenstorrent_query_mappings_out),
     ]

class struct_tenstorrent_allocate_dma_buf_in(Structure):
    pass

struct_tenstorrent_allocate_dma_buf_in._pack_ = 1 # source:False
struct_tenstorrent_allocate_dma_buf_in._fields_ = [
    ('requested_size', ctypes.c_uint32),
    ('buf_index', ctypes.c_ubyte),
    ('reserved0', ctypes.c_ubyte * 3),
    ('reserved1', ctypes.c_uint64 * 2),
]

class struct_tenstorrent_allocate_dma_buf_out(Structure):
    pass

struct_tenstorrent_allocate_dma_buf_out._pack_ = 1 # source:False
struct_tenstorrent_allocate_dma_buf_out._fields_ = [
    ('physical_address', ctypes.c_uint64),
    ('mapping_offset', ctypes.c_uint64),
    ('size', ctypes.c_uint32),
    ('reserved0', ctypes.c_uint32),
    ('reserved1', ctypes.c_uint64 * 2),
]

class struct_tenstorrent_allocate_dma_buf(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_allocate_dma_buf_in),
    ('out', struct_tenstorrent_allocate_dma_buf_out),
     ]

class struct_tenstorrent_free_dma_buf_in(Structure):
    pass

class struct_tenstorrent_free_dma_buf_out(Structure):
    pass

class struct_tenstorrent_free_dma_buf(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_free_dma_buf_in),
    ('out', struct_tenstorrent_free_dma_buf_out),
     ]

class struct_tenstorrent_get_driver_info_in(Structure):
    pass

struct_tenstorrent_get_driver_info_in._pack_ = 1 # source:False
struct_tenstorrent_get_driver_info_in._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
]

class struct_tenstorrent_get_driver_info_out(Structure):
    pass

struct_tenstorrent_get_driver_info_out._pack_ = 1 # source:False
struct_tenstorrent_get_driver_info_out._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('driver_version', ctypes.c_uint32),
]

class struct_tenstorrent_get_driver_info(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_get_driver_info_in),
    ('out', struct_tenstorrent_get_driver_info_out),
     ]

class struct_tenstorrent_reset_device_in(Structure):
    pass

struct_tenstorrent_reset_device_in._pack_ = 1 # source:False
struct_tenstorrent_reset_device_in._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

class struct_tenstorrent_reset_device_out(Structure):
    pass

struct_tenstorrent_reset_device_out._pack_ = 1 # source:False
struct_tenstorrent_reset_device_out._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('result', ctypes.c_uint32),
]

class struct_tenstorrent_reset_device(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_reset_device_in),
    ('out', struct_tenstorrent_reset_device_out),
     ]

class struct_tenstorrent_pin_pages_in(Structure):
    pass

struct_tenstorrent_pin_pages_in._pack_ = 1 # source:False
struct_tenstorrent_pin_pages_in._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('virtual_address', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
]

class struct_tenstorrent_pin_pages_out(Structure):
    pass

struct_tenstorrent_pin_pages_out._pack_ = 1 # source:False
struct_tenstorrent_pin_pages_out._fields_ = [
    ('physical_address', ctypes.c_uint64),
]

class struct_tenstorrent_pin_pages_out_extended(Structure):
    pass

struct_tenstorrent_pin_pages_out_extended._pack_ = 1 # source:False
struct_tenstorrent_pin_pages_out_extended._fields_ = [
    ('physical_address', ctypes.c_uint64),
    ('noc_address', ctypes.c_uint64),
]

class struct_tenstorrent_unpin_pages_in(Structure):
    pass

struct_tenstorrent_unpin_pages_in._pack_ = 1 # source:False
struct_tenstorrent_unpin_pages_in._fields_ = [
    ('virtual_address', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64),
]

class struct_tenstorrent_unpin_pages_out(Structure):
    pass

class struct_tenstorrent_unpin_pages(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_unpin_pages_in),
    ('out', struct_tenstorrent_unpin_pages_out),
     ]

class struct_tenstorrent_pin_pages(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_pin_pages_in),
    ('out', struct_tenstorrent_pin_pages_out),
     ]

class struct_tenstorrent_lock_ctl_in(Structure):
    pass

struct_tenstorrent_lock_ctl_in._pack_ = 1 # source:False
struct_tenstorrent_lock_ctl_in._fields_ = [
    ('output_size_bytes', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('index', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_tenstorrent_lock_ctl_out(Structure):
    pass

struct_tenstorrent_lock_ctl_out._pack_ = 1 # source:False
struct_tenstorrent_lock_ctl_out._fields_ = [
    ('value', ctypes.c_ubyte),
]

class struct_tenstorrent_lock_ctl(Structure):
    pass

struct_tenstorrent_lock_ctl._pack_ = 1 # source:False
struct_tenstorrent_lock_ctl._fields_ = [
    ('in', struct_tenstorrent_lock_ctl_in),
    ('out', struct_tenstorrent_lock_ctl_out),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_tenstorrent_map_peer_bar_in(Structure):
    pass

struct_tenstorrent_map_peer_bar_in._pack_ = 1 # source:False
struct_tenstorrent_map_peer_bar_in._fields_ = [
    ('peer_fd', ctypes.c_uint32),
    ('peer_bar_index', ctypes.c_uint32),
    ('peer_bar_offset', ctypes.c_uint32),
    ('peer_bar_length', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

class struct_tenstorrent_map_peer_bar_out(Structure):
    pass

struct_tenstorrent_map_peer_bar_out._pack_ = 1 # source:False
struct_tenstorrent_map_peer_bar_out._fields_ = [
    ('dma_address', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64),
]

class struct_tenstorrent_map_peer_bar(Structure):
    pass

struct_tenstorrent_map_peer_bar._pack_ = 1 # source:False
struct_tenstorrent_map_peer_bar._fields_ = [
    ('in', struct_tenstorrent_map_peer_bar_in),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('out', struct_tenstorrent_map_peer_bar_out),
]

class struct_tenstorrent_allocate_tlb_in(Structure):
    pass

struct_tenstorrent_allocate_tlb_in._pack_ = 1 # source:False
struct_tenstorrent_allocate_tlb_in._fields_ = [
    ('size', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64),
]

class struct_tenstorrent_allocate_tlb_out(Structure):
    pass

struct_tenstorrent_allocate_tlb_out._pack_ = 1 # source:False
struct_tenstorrent_allocate_tlb_out._fields_ = [
    ('id', ctypes.c_uint32),
    ('reserved0', ctypes.c_uint32),
    ('mmap_offset_uc', ctypes.c_uint64),
    ('mmap_offset_wc', ctypes.c_uint64),
    ('reserved1', ctypes.c_uint64),
]

class struct_tenstorrent_allocate_tlb(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_allocate_tlb_in),
    ('out', struct_tenstorrent_allocate_tlb_out),
     ]

class struct_tenstorrent_free_tlb_in(Structure):
    pass

struct_tenstorrent_free_tlb_in._pack_ = 1 # source:False
struct_tenstorrent_free_tlb_in._fields_ = [
    ('id', ctypes.c_uint32),
]

class struct_tenstorrent_free_tlb_out(Structure):
    pass

class struct_tenstorrent_free_tlb(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_free_tlb_in),
    ('out', struct_tenstorrent_free_tlb_out),
     ]

class struct_tenstorrent_noc_tlb_config(Structure):
    pass

struct_tenstorrent_noc_tlb_config._pack_ = 1 # source:False
struct_tenstorrent_noc_tlb_config._fields_ = [
    ('addr', ctypes.c_uint64),
    ('x_end', ctypes.c_uint16),
    ('y_end', ctypes.c_uint16),
    ('x_start', ctypes.c_uint16),
    ('y_start', ctypes.c_uint16),
    ('noc', ctypes.c_ubyte),
    ('mcast', ctypes.c_ubyte),
    ('ordering', ctypes.c_ubyte),
    ('linked', ctypes.c_ubyte),
    ('static_vc', ctypes.c_ubyte),
    ('reserved0', ctypes.c_ubyte * 3),
    ('reserved1', ctypes.c_uint32 * 2),
]

class struct_tenstorrent_configure_tlb_in(Structure):
    pass

struct_tenstorrent_configure_tlb_in._pack_ = 1 # source:False
struct_tenstorrent_configure_tlb_in._fields_ = [
    ('id', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('config', struct_tenstorrent_noc_tlb_config),
]

class struct_tenstorrent_configure_tlb_out(Structure):
    pass

struct_tenstorrent_configure_tlb_out._pack_ = 1 # source:False
struct_tenstorrent_configure_tlb_out._fields_ = [
    ('reserved', ctypes.c_uint64),
]

class struct_tenstorrent_configure_tlb(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('in', struct_tenstorrent_configure_tlb_in),
    ('out', struct_tenstorrent_configure_tlb_out),
     ]

__all__ = \
    ['TENSTORRENT_DRIVER_VERSION', 'TENSTORRENT_IOCTL_MAGIC',
    'TENSTORRENT_LOCK_CTL_ACQUIRE', 'TENSTORRENT_LOCK_CTL_RELEASE',
    'TENSTORRENT_LOCK_CTL_TEST', 'TENSTORRENT_MAPPING_RESOURCE0_UC',
    'TENSTORRENT_MAPPING_RESOURCE0_WC',
    'TENSTORRENT_MAPPING_RESOURCE1_UC',
    'TENSTORRENT_MAPPING_RESOURCE1_WC',
    'TENSTORRENT_MAPPING_RESOURCE2_UC',
    'TENSTORRENT_MAPPING_RESOURCE2_WC', 'TENSTORRENT_MAPPING_UNUSED',
    'TENSTORRENT_MAX_DMA_BUFS', 'TENSTORRENT_MAX_INBOUND_TLBS',
    'TENSTORRENT_PIN_PAGES_CONTIGUOUS',
    'TENSTORRENT_PIN_PAGES_NOC_DMA',
    'TENSTORRENT_PIN_PAGES_NOC_TOP_DOWN',
    'TENSTORRENT_RESET_DEVICE_CONFIG_WRITE',
    'TENSTORRENT_RESET_DEVICE_RESET_PCIE_LINK',
    'TENSTORRENT_RESET_DEVICE_RESTORE_STATE',
    'TENSTORRENT_RESOURCE_LOCK_COUNT', 'TTDRIVER_IOCTL_H_INCLUDED',
    '_IO', '_IOR', '_IOW', '_IOWR',
    'struct_tenstorrent_allocate_dma_buf',
    'struct_tenstorrent_allocate_dma_buf_in',
    'struct_tenstorrent_allocate_dma_buf_out',
    'struct_tenstorrent_allocate_tlb',
    'struct_tenstorrent_allocate_tlb_in',
    'struct_tenstorrent_allocate_tlb_out',
    'struct_tenstorrent_configure_tlb',
    'struct_tenstorrent_configure_tlb_in',
    'struct_tenstorrent_configure_tlb_out',
    'struct_tenstorrent_free_dma_buf',
    'struct_tenstorrent_free_dma_buf_in',
    'struct_tenstorrent_free_dma_buf_out',
    'struct_tenstorrent_free_tlb', 'struct_tenstorrent_free_tlb_in',
    'struct_tenstorrent_free_tlb_out',
    'struct_tenstorrent_get_device_info',
    'struct_tenstorrent_get_device_info_in',
    'struct_tenstorrent_get_device_info_out',
    'struct_tenstorrent_get_driver_info',
    'struct_tenstorrent_get_driver_info_in',
    'struct_tenstorrent_get_driver_info_out',
    'struct_tenstorrent_lock_ctl', 'struct_tenstorrent_lock_ctl_in',
    'struct_tenstorrent_lock_ctl_out',
    'struct_tenstorrent_map_peer_bar',
    'struct_tenstorrent_map_peer_bar_in',
    'struct_tenstorrent_map_peer_bar_out',
    'struct_tenstorrent_mapping', 'struct_tenstorrent_noc_tlb_config',
    'struct_tenstorrent_pin_pages', 'struct_tenstorrent_pin_pages_in',
    'struct_tenstorrent_pin_pages_out',
    'struct_tenstorrent_pin_pages_out_extended',
    'struct_tenstorrent_query_mappings',
    'struct_tenstorrent_query_mappings_in',
    'struct_tenstorrent_query_mappings_out',
    'struct_tenstorrent_reset_device',
    'struct_tenstorrent_reset_device_in',
    'struct_tenstorrent_reset_device_out',
    'struct_tenstorrent_unpin_pages',
    'struct_tenstorrent_unpin_pages_in',
    'struct_tenstorrent_unpin_pages_out']
