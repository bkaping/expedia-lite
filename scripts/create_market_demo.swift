// Encode the actual browser screenshot sequence as a captioned, silent 40s MP4.
// No generated market imagery. Requires macOS's bundled Swift/AppKit/AVFoundation.
import AppKit
import AVFoundation
import CoreVideo

let frames = CommandLine.arguments[1]
let output = URL(fileURLWithPath: CommandLine.arguments[2])
let width = 1440, height = 1640
let writer = try AVAssetWriter(outputURL: output, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width, AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 1800000, AVVideoMaxKeyFrameIntervalKey: 10]
])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height,
    kCVPixelBufferCGImageCompatibilityKey as String: true,
    kCVPixelBufferCGBitmapContextCompatibilityKey as String: true
])
writer.add(input)
guard writer.startWriting() else { fatalError("Cannot start encoder: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)
for index in 0..<40 {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.01) }
    let url = URL(fileURLWithPath: frames).appendingPathComponent(String(format: "frame-%03d.png", index))
    let image = NSImage(contentsOf: url)!
    var rect = CGRect(origin: .zero, size: image.size)
    let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil)!
    var buffer: CVPixelBuffer?
    CVPixelBufferCreate(nil, width, height, kCVPixelFormatType_32ARGB, [kCVPixelBufferCGImageCompatibilityKey as String:true, kCVPixelBufferCGBitmapContextCompatibilityKey as String:true] as CFDictionary, &buffer)
    let pixel = buffer!
    CVPixelBufferLockBaseAddress(pixel, [])
    let context = CGContext(data: CVPixelBufferGetBaseAddress(pixel), width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pixel), space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    context.setFillColor(CGColor(red: 0.04, green: 0.08, blue: 0.12, alpha: 1))
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    let scale = min(Double(width)/Double(cgImage.width), Double(height-125)/Double(cgImage.height))
    let imageWidth = Double(cgImage.width)*scale, imageHeight = Double(cgImage.height)*scale
    context.draw(cgImage, in: CGRect(x: (Double(width)-imageWidth)/2, y: Double(height)-imageHeight, width: imageWidth, height: imageHeight))
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)
    let title: String
    let detail: String
    switch index {
    case 0..<12:
        title = "PART 4.1 · REAL YAHOO FINANCE → FASTAPI → SQLITE → WEBSOCKET CHART"
        detail = "Live source age and stored candle revisions. Volume is Yahoo's observed counter delta; zero is not proof of no trading."
    case 12..<20:
        title = "UNAVAILABLE FEED · STORED OBSERVATIONS REMAIN VISIBLE"
        detail = "Deliberate source disconnection. The backend stays reachable; data age continues increasing. No synthetic fallback."
    case 20..<32:
        title = "RECORDED REPLAY · SAVED REVISIONS, IN RECEIPT ORDER"
        detail = "Design decision: replay starts empty and stops at a captured event boundary. Closed/forming flags are historical."
    default:
        title = "LIVE SOURCE RESTORED · VERIFIED AGAINST SQLITE"
        detail = "Verification: actual WebSocket candle matched its SQLite event; replay matched the saved boundary. 33 tests + build pass."
    }
    let paragraph = NSMutableParagraphStyle(); paragraph.lineBreakMode = .byWordWrapping
    (title as NSString).draw(in: CGRect(x: 28, y: 72, width: 1384, height: 35), withAttributes: [.font:NSFont.boldSystemFont(ofSize:21),.foregroundColor:NSColor(calibratedRed:0.55,green:0.88,blue:0.78,alpha:1),.paragraphStyle:paragraph])
    (detail as NSString).draw(in: CGRect(x: 28, y: 16, width: 1384, height: 48), withAttributes: [.font:NSFont.systemFont(ofSize:20),.foregroundColor:NSColor.white,.paragraphStyle:paragraph])
    NSGraphicsContext.restoreGraphicsState()
    CVPixelBufferUnlockBaseAddress(pixel, [])
    if !adaptor.append(pixel, withPresentationTime: CMTime(value: Int64(index), timescale: 1)) {
        fatalError("Frame encoding failed: \(String(describing: writer.error))")
    }
}
writer.endSession(atSourceTime: CMTime(value: 40, timescale: 1))
input.markAsFinished()
let semaphore = DispatchSemaphore(value: 0)
writer.finishWriting { semaphore.signal() }
semaphore.wait()
guard writer.status == .completed else { fatalError("Video failed: \(String(describing: writer.error))") }
print("Encoded 40 seconds of actual browser captures: \(output.path)")
