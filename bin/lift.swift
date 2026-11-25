import Foundation
import Vision
import CoreImage
import AppKit
// lift <in> <out.png>: the macOS "lift subject" cut-out (Vision foreground instance mask)
let a = CommandLine.arguments
let ci = CIImage(contentsOf: URL(fileURLWithPath: a[1]))!
let h = VNImageRequestHandler(ciImage: ci)
let r = VNGenerateForegroundInstanceMaskRequest()
try h.perform([r])
guard let o = r.results?.first else { print("no subject"); exit(1) }
let buf = try o.generateMaskedImage(ofInstances: o.allInstances, from: h, croppedToInstancesExtent: true)
let out = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: a[2]), format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())
print("ok", o.allInstances.count)
