class LinearPCMProcessor extends AudioWorkletProcessor {
  static BUFFER_SIZE = 8192;

  buffer;
  offset;

  constructor() {
    super();
    this.buffer = new Int16Array(LinearPCMProcessor.BUFFER_SIZE);
    this.offset = 0;
  }

  /**
   * Converts input data from Float32Array to Int16Array, stores it to the buffer,
   * and posts to the main thread when the buffer is full.
   */
  process(inputList, _outputList, _parameters) {
    if (!inputList || inputList.length === 0) return true;

    const inputChannel = inputList[0][0]; // first channel of first input
    if (!inputChannel) return true;

    for (let i = 0; i < inputChannel.length; i++) {
      const sample = Math.max(-1, Math.min(1, inputChannel[i]));
      this.buffer[i + this.offset] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }

    this.offset += inputChannel.length;

    if (this.offset >= this.buffer.length) {
      this.flush();
    }

    return true;
  }

  /**
   * Sends the buffer's content to the main thread via postMessage(), then resets offset.
   */
  flush() {
    this.port.postMessage(this.buffer);
    this.offset = 0;
  }
}

registerProcessor("linear-pcm-processor", LinearPCMProcessor);
export { };
