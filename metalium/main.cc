#include <tt-metalium/mesh_device.hpp>
//#include <tt-metalium/device.hpp>
//#include <tt-metalium/distributed.hpp>
//using namespace tt;

int main() {
  constexpr int device_id = 0;
  //auto device = tt_metal::CreateDevice(device_id);
  auto device = tt::tt_metal::distributed::MeshDevice::create_unit_mesh(device_id);
}