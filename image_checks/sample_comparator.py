"""Module for in memory pixel comparisons."""

import nuke


class SampleComparator:
    """Image comparator that uses nuke.sample for processing image data.

    This comparison is quite slow. It needs to compute the full image of both nodes.
    """

    def __init__(self):
        pass

    @staticmethod
    def assert_equal(node_a: nuke.Node, node_b: nuke.Node) -> None:
        """Assert that both nodes output the same pixels.

        Args:
        ----
            node_a: first test node.
            node_b: second test node.

        Raises:
        ------
            AssertionError: the two nodes are not equal based on the testing criteria.

        """
        all_channels = set(node_a.channels()).union(node_b.channels())
        a_format = node_a.format()
        b_format = node_b.format()
        assert a_format.x() == b_format.x()
        assert a_format.y() == b_format.y()
        assert a_format.r() == b_format.r()
        assert a_format.t() == b_format.t()

        left = a_format.x()
        bottom = a_format.y()
        right = a_format.r()
        top = a_format.t()

        slice_w = 100  # px
        slice_d = slice_w / 2
        for channel in all_channels:
            for point_x in range(left, right + slice_w, slice_w):
                for point_y in range(bottom, top + slice_w, slice_w):
                    a_sample = node_a.sample(
                        channel,
                        point_x + 0.5,
                        point_y + 0.5,
                        slice_d,
                        slice_d,
                    )
                    b_sample = node_b.sample(
                        channel,
                        point_x + 0.5,
                        point_y + 0.5,
                        slice_d,
                        slice_d,
                    )
                    assert a_sample == b_sample, f"Point({point_x},{point_y}): {a_sample} != {b_sample}"
