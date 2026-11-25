// Face and object finder for the Vetto Video Engine (Apple Vision, on-device, nothing is downloaded).
// Build: swiftc -O engine/vision.swift -o bin/vision
// Use:   bin/vision frame1.jpg frame2.jpg ...   → JSON: [{"faces":[[x,y,w,h]], "objects":[[x,y,w,h]], "hands":[[x,y,w,h]]}, ...]
// Boxes are normalised 0..1 with the origin at the TOP-left (Vision's is bottom-left; flipped here).
import Foundation
import Vision
import AppKit

func flip(_ r: CGRect) -> [Double] {
    return [Double(r.origin.x), Double(1 - r.origin.y - r.size.height), Double(r.size.width), Double(r.size.height)]
}

var out: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
    var entry: [String: Any] = ["faces": [], "objects": [], "hands": []]
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { out.append(entry); continue }
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    let faces = VNDetectFaceRectanglesRequest()
    let objects = VNGenerateObjectnessBasedSaliencyImageRequest()
    let hands = VNDetectHumanHandPoseRequest()
    hands.maximumHandCount = 2
    try? handler.perform([faces, objects, hands])
    // a hand = the box around its confident joints (an object held or pointed at sits there)
    entry["hands"] = (hands.results ?? []).compactMap { obs -> [Double]? in
        guard let pts = try? obs.recognizedPoints(.all) else { return nil }
        let good = pts.values.filter { $0.confidence > 0.3 }
        if good.count < 4 { return nil }
        let xs = good.map { $0.location.x }, ys = good.map { $0.location.y }
        let r = CGRect(x: xs.min()!, y: ys.min()!, width: xs.max()! - xs.min()!, height: ys.max()! - ys.min()!)
        return flip(r)
    }
    entry["faces"] = (faces.results ?? []).map { flip($0.boundingBox) }
    if let sal = objects.results?.first as? VNSaliencyImageObservation {
        entry["objects"] = (sal.salientObjects ?? []).map { flip($0.boundingBox) }
    }
    out.append(entry)
}
let data = try JSONSerialization.data(withJSONObject: out, options: [])
print(String(data: data, encoding: .utf8)!)
