#include <tt-metalium/mesh_device.hpp>
#include <tt-metalium/host_api.hpp>
#include <tt-metalium/device.hpp>

using namespace tt::tt_metal;

int main() {
  constexpr int device_id = 0;
  IDevice* device = CreateDevice(device_id);
  CommandQueue& cq = device->command_queue();
  Program program = CreateProgram();

  constexpr CoreCoord core = {0, 0};
  KernelHandle dram_copy_kernel_id = CreateKernel(program, "loopback_dram_copy.cpp", core,
    DataMovementConfig{.processor = DataMovementProcessor::RISCV_0, .noc = NOC::RISCV_0_default});

  constexpr uint32_t single_tile_size = 2 * (32 * 32);
  constexpr uint32_t num_tiles = 50;
  constexpr uint32_t dram_buffer_size = single_tile_size * num_tiles;

  tt::tt_metal::InterleavedBufferConfig dram_config{
    .device = device,
    .size = dram_buffer_size,
    .page_size = dram_buffer_size,
    .buffer_type = tt::tt_metal::BufferType::DRAM};
  tt::tt_metal::InterleavedBufferConfig l1_config{
    .device = device,
    .size = dram_buffer_size,
    .page_size = dram_buffer_size,
    .buffer_type = tt::tt_metal::BufferType::L1};

  auto l1_buffer = CreateBuffer(l1_config);

  auto input_dram_buffer = CreateBuffer(dram_config);
  const uint32_t input_dram_buffer_addr = input_dram_buffer->address();

  auto output_dram_buffer = CreateBuffer(dram_config);
  const uint32_t output_dram_buffer_addr = output_dram_buffer->address();

  // Since all interleaved buffers have size == page_size, they are entirely contained in the first DRAM bank
  const uint32_t input_bank_id = 0;
  const uint32_t output_bank_id = 0;

  std::vector<uint32_t> input_vec = create_random_vector_of_bfloat16(
      dram_buffer_size, 100, std::chrono::system_clock::now().time_since_epoch().count());
  EnqueueWriteBuffer(cq, input_dram_buffer, input_vec, false);

  const std::vector<uint32_t> runtime_args = {
    l1_buffer->address(),
    input_dram_buffer->address(),
    input_bank_id,
    output_dram_buffer->address(),
    output_bank_id,
    (uint32_t)l1_buffer->size()};
  SetRuntimeArgs(program, dram_copy_kernel_id, core, runtime_args);

  EnqueueProgram(cq, program, false);
  Finish(cq);

  std::vector<uint32_t> result_vec;
  EnqueueReadBuffer(cq, output_dram_buffer, result_vec, true);

  if (input_vec == result_vec) {
    printf("passed!\n");
  } else {
    printf("FAILED :(\n");
  }
  CloseDevice(device);
}
