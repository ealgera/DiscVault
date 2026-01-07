<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats } from 'html5-qrcode'

const emit = defineEmits(['scan-success', 'scan-error'])

const scannerId = 'html5-qrcode-reader'
let html5QrcodeScanner: Html5QrcodeScanner | null = null

function onScanSuccess(decodedText: string, decodedResult: any) {
  // Voorkom dubbele scans kort achter elkaar indien nodig, 
  // maar de library heeft hier vaak settings voor.
  emit('scan-success', decodedText)
}

function onScanFailure(error: any) {
  // Dit vuurt heel vaak (elke frame dat er geen barcode is), dus meestal negeren we dit in de UI
  // emit('scan-error', error)
}

onMounted(() => {
  const config = {
    fps: 10,
    qrbox: { width: 250, height: 250 },
    aspectRatio: 1.0,
    formatsToSupport: [ 
        Html5QrcodeSupportedFormats.EAN_13, 
        Html5QrcodeSupportedFormats.EAN_8,
        Html5QrcodeSupportedFormats.UPC_A,
        Html5QrcodeSupportedFormats.UPC_E 
    ]
  }
  
  // verbose=false
  html5QrcodeScanner = new Html5QrcodeScanner(scannerId, config, false)
  html5QrcodeScanner.render(onScanSuccess, onScanFailure)
})

onUnmounted(() => {
  if (html5QrcodeScanner) {
    html5QrcodeScanner.clear().catch(error => {
      console.error("Failed to clear html5QrcodeScanner. ", error)
    })
  }
})
</script>

<template>
  <div class="w-full overflow-hidden rounded-xl bg-black relative">
    <div :id="scannerId" class="w-full h-full"></div>
    <!-- Overlay instructie -->
    <div class="absolute bottom-4 left-0 right-0 text-center pointer-events-none">
        <span class="bg-black/50 text-white px-3 py-1 rounded-full text-sm backdrop-blur-sm">
            Richt op de streepjescode
        </span>
    </div>
  </div>
</template>

<style>
/* Custom styling om de scanner UI van de library iets strakker te maken */
#html5-qrcode-reader {
    border: none !important;
}
#html5-qrcode-reader__scan_region {
    
}
#html5-qrcode-reader__dashboard_section_csr button {
    @apply bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium mt-2;
}
#html5-qrcode-reader__dashboard_section_swaplink {
    @apply text-primary text-sm underline decoration-primary mt-2 block;
}
</style>
