"""
Assignment 2 - Sample Tests

=== CSC148 Summer 2023 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith,
                   Andrea Mitchell, Bahar Aameri

=== Module Description ===
This module contains sample tests for Assignment 2, Tasks 1 and 2.
The tests use the provided example-directory, so make sure you have downloaded
and extracted it into the same place as this test file.
This test suite is very small. You should plan to add to it significantly to
thoroughly test your code.

IMPORTANT NOTES:
    - If using PyCharm, go into your Settings window, and go to
      Editor -> General.
      Make sure the "Ensure line feed at file end on Save" is NOT checked.
      Then, make sure none of the example files have a blank line at the end.
      (If they do, the data size will be off.)

    - os.listdir behaves differently on different
      operating systems.  These tests expect the outcomes that one gets
      when running on the *Teaching Lab machines*.
      Please run all of your tests there - otherwise,
      you might get inaccurate test failures!

    - Depending on your operating system or other system settings, you
      may end up with other files in your example-directory that will cause
      inaccurate test failures. That will not happen on the Teachin Lab
      machines.  This is a second reason why you should run this test module
      there.
"""
import os

from hypothesis import given
from hypothesis.strategies import integers

from tm_trees import TMTree, FileSystemTree

# This should be the path to the "workshop" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
EXAMPLE_PATH = os.path.join(os.getcwd(), 'example-directory', 'workshop')


# TEST 1 -----------------------------------------------------------------------
def test_single_file() -> None:
    """Test a tree with a single file.
    This is a test for the TMTree and FileSystemTree initializers.

    This should pass after TASK 1 is complete.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)


# TEST 2 -----------------------------------------------------------------------
def test_example_data() -> None:
    """Test the root of the tree at the 'workshop' folder in the example data
    This is a test for the TMTree and FileSystemTree initializers.

    This should pass after TASK 1 is complete.
    """
    tree = FileSystemTree(EXAMPLE_PATH)

    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)

    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree


# TEST 3 -----------------------------------------------------------------------
@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    """Test that the correct rectangle is produced for a single file.
    This is a test for the update_rectangles and the get_rectangles methods.

    This should pass when TASK 2 is complete.
    """
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()
    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)


# TEST 4 -----------------------------------------------------------------------
def test_example_data_rectangles() -> None:
    """This test sorts the subtrees, because different operating systems have
    different behaviours with os.listdir.

    You should *NOT* do any sorting in your own code

    This should pass after TASK 2 is complete.
    NOTE! This should FAIL after TASK 6 is complete.
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.update_rectangles((0, 0, 200, 100))
    rects = tree.get_rectangles()

    assert len(rects) == 6

    # UPDATED:
    # Here, we illustrate the correct order of the returned rectangles.
    # Note that this corresponds to the folder contents always being
    # sorted in alphabetical order. This is enforced in these sample tests
    # only so that you can run them on your own computer, rather than on
    # the Teaching Labs.
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
                      (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


# TEST 5 -----------------------------------------------------------------------
def test_update_colours_and_depths() -> None:
    """Builds a tree using the example path, and sorts it for testing purposes.
    Tests that the update_colours_and_depths successfully updated the _colours
    and _depths attributes for internal tree nodes.

    This should pass after TASK 5 is complete.
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.update_colours_and_depths()
    results = tree.tree_traversal()
    assert results == [('workshop', 0, (0, 0, 0)),
                       ('activities', 1, (100, 100, 100)),
                       ('images', 2, (200, 200, 200)),
                       ('prep', 1, (100, 100, 100)),
                       ('images', 2, (200, 200, 200))]


# TEST 6 -----------------------------------------------------------------------
def test_extra_test() -> None:
    """This is an extra test added for your own testing purposes. You may find
    it useful to modify the tree_traversal() method to show you different
    attributes from the nodes.
    """
    tree = FileSystemTree(EXAMPLE_PATH)
    # print(tree.tree_traversal())
    assert 1 == 1


##############################################################################
# Helpers
##############################################################################

def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    """Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TMTree) -> None:
    """Sort the subtrees of <tree> in alphabetical order.
    THIS IS FOR THE PURPOSES OF THE SAMPLE TEST ONLY; YOU SHOULD NOT SORT
    YOUR SUBTREES IN THIS WAY. This allows the sample test to run on different
    operating systems.

    This is recursive, and affects all levels of the tree.
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest
    pytest.main(['a2_sample_test.py'])
