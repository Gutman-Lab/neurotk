from histomicstk.cli.utils import CLIArgumentParser
from pprint import pprint
import large_image, json
from transformers import SegformerForSemanticSegmentation
from dsa_helpers.ml.segformer_semantic_segmentation import inference


def main(args):
    """Tissue segmentation at a low resolution scale using SegFormer for
    semantic segmentation (HuggingFace implementation). The output is scaled
    back to the original resolution and saved as DSA annotations.

    args:
        The CLI arguments.
        - docname: The name of the annotation document saved as output.
        - inputImageFile: Filepath to the WSI.
        - mag: Magnification level the thumbnail to perform segmentation.
        - tile_size: The size of the tiles to be used for segmentation.
        - batch_size: The batch size to be used for segmentation.
        - outputAnnotationFile: Filepath to save the output annotation.

    """
    # Print the CLI arguments.
    pprint(vars(args))

    # Get the tile source.
    ts = large_image.getTileSource(args.inputImageFile)

    kwargs = {
        "scale": {"magnification": 2.0},
        "format": large_image.tilesource.TILE_FORMAT_NUMPY,
    }

    print("Getting thumbnail image...")
    thumbnail_img = ts.getRegion(**kwargs)[0][:, :, :3]
    print(f"   Thumbnail image obtained of shape: {thumbnail_img.shape}.")

    # Create the map between of labels.
    id2label = {0: "background", 1: "tissue"}
    label2id = {v: k for k, v in id2label.items()}

    # Load the model.
    print("Loading model...")
    model = SegformerForSemanticSegmentation.from_pretrained(
        "TissueSegmentation/model", id2label=id2label, label2id=label2id
    )

    # Run inference.
    print("Running inference...")
    contours = inference(
        thumbnail_img, model, tile_size=args.tile_size, batch_size=args.batch_size
    )[1]

    # Convert the contours to DSA-style elements.
    print("Pushing results as annotations...")
    elements = []

    # Calculate the scale factor to go from low mag -> high mag coordinates.
    sf = ts.getMetadata()["magnification"] / args.mag

    for contour in contours:
        # Remove the single-dimensional entries.
        contour = contour.squeeze()

        # Convert to list of [x, y, 0] tuples.
        contour_tuples = [
            (int(point[0] * sf), int(point[1] * sf), 0) for point in contour
        ]

        elements.append(
            {
                "fillColor": "rgba(0, 255, 0, 0.25)",
                "lineColor": "rgb(0, 255, 0)",
                "lineWidth": 4,
                "type": "polyline",
                "closed": True,
                "points": contour_tuples,
                "label": {"value": "predicted tissue"},
                "group": "tissue",
            }
        )

    # Create an annotation dictionary
    ann_doc = {
        "name": args.docname,
        "elements": elements,
        "attributes": {
            "params": vars(args),
        },
    }

    pprint(ann_doc)

    # Save the annotation dictionary to the output annotation file
    with open(args.outputAnnotationFile, "w") as fh:
        json.dump(ann_doc, fh, separators=(",", ":"), sort_keys=False)

    print("Done!")


if __name__ == "__main__":
    # Run main function, passing CLI arguments.
    main(CLIArgumentParser().parse_args())
