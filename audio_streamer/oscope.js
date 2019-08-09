
class OScope {
  constructor(sampleRate) {
    this.sampleRate = sampleRate;
    this.x = [];
    this.y = [];
    this.clear();
  }

  clear(){
    this.x.splice(0, this.x.length);
    this.y.splice(0, this.y.length);
    for(i=0; i < this.sampleRate; i++){
        this.x.push(-i/this.sampleRate);
        this.y.push(0);
    }
  }

  rollData(buffer, values, size){
      Array.prototype.push.apply(buffer, values);
      var length = buffer.length;
      if(length >= size){
          buffer.splice(0, length - size);
          return true;
      }
      return false;
  }

  addData(values){
      this.rollData(this.y, values, this.sampleRate);
  }
}


function calculate_freq_bins(sampleRate, nfft){
    var freq_bins = [];
    var step = sampleRate / nfft;
    var i;

    for(i=1; i < sampleRate/2;){
        i += step;
        freq_bins.push(i);
    }
    return freq_bins;
}