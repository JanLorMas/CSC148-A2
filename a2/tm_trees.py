"""
Assignment 2: Trees for Treemap

=== CSC148 Summer 2023 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith, Andrea Mitchell,
                   Bahar Aameri

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


def get_colour() -> Tuple[int, int, int]:
    """This function picks a random colour selectively such that it is not on
    the grey scale. The colour is close to the grey scale if the r g b
    values have a small variance. This function checks if all the numbers
    are close to the mean, if so, it shifts the last digit by 150.

    This way you can't confuse the leaf rectangles with folder rectangles,
    because the leaves will always be a colour, never close to black / white.
    """
    rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    avg = sum(rgb) // 3
    count = 0
    for item in rgb:
        if abs(item - avg) < 20:
            count += 1
    if count == 3:
        rgb[2] = (rgb[2] + 150) % 255
    return tuple(rgb)


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect: The pygame rectangle representing this node in the visualization.
    data_size: The size of the data represented by this tree.

    === Private Attributes ===
    _colour: The RGB colour value of the root of this tree.
    _name: The root value of this tree, or None if this tree is empty.
    _subtrees: The subtrees of this tree.
    _parent_tree: The parent tree of this tree; i.e., the tree that contains
    this tree as a subtree, or None if this tree is not part of a larger tree.
    _expanded: Whether this tree is considered expanded for visualization.
    _depth: The depth of this tree node in relation to the root.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - _colour's elements are each in the range 0-255.
    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - if _parent_tree is not None, then self is in _parent_tree._subtrees
    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool
    _depth: int

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initializes a new TMTree with a random colour, the provided name
        and sets the subtrees to the list of provided subtrees. Sets this tree
        as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self._expanded = False
        self.rect = (0, 0, 0, 0)
        self._parent_tree = None
        self._depth = 0
        if name is not None:
            self._name = name
            self._colour = get_colour()
            self._subtrees = subtrees
            if not self._subtrees:
                self.data_size = data_size
            else:
                self.data_size = 0
                for subtree in self._subtrees:
                    self.data_size += subtree.data_size
                    subtree._parent_tree = self
        else:
            self._name = name
            self._colour = get_colour()
            self._subtrees = []
            self._parent_tree = None
            self._expanded = False
            self.data_size = data_size

    def is_empty(self) -> bool:
        """Returns True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    # **************************************************************************
    # ************* TASK 2: UPDATE AND GET RECTANGLES **************************
    # **************************************************************************

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Updates the rectangles in this tree and its descendants using the
        treemap algorithm to fill the area defined by the <rect> parameter.
        """
        x, y, width, height = rect
        pushed_y, pushed_x = 0, 0

        if self.data_size == 0:
            self.rect = (0, 0, 0, 0)
        elif not self._subtrees:
            self.rect = rect
        else:
            # Go through all subtrees except the last one
            # Create a new rectangle based upon the percentage
            # the of data the file takes up and position
            # relative to the previous rectangles
            if width > height:
                self.rect = rect
                for subtree in self._subtrees[:-1]:
                    percentage = subtree.data_size / self.data_size
                    new_width = math.floor(percentage * width)
                    new_rec = (x + pushed_x, y, new_width, height)
                    subtree.update_rectangles(new_rec)
                    pushed_x += new_width
                remaining_space = width - pushed_x
                remaining_rec = (x + pushed_x, y, remaining_space, height)
                self._subtrees[-1].update_rectangles(remaining_rec)
            else:
                self.rect = rect
                for subtree in self._subtrees[:-1]:
                    percentage = subtree.data_size / self.data_size
                    new_height = math.floor(percentage * height)
                    new_rec = (x, y + pushed_y, width, new_height)
                    subtree.update_rectangles(new_rec)
                    pushed_y += new_height
                remaining_space = height - pushed_y
                remaining_rec = (x, y + pushed_y, width, remaining_space)
                self._subtrees[-1].update_rectangles(remaining_rec)

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Returns a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        gr_list = []
        if not self._subtrees:
            return [(self.rect, self._colour)]
        elif not self._expanded:
            return [(self.rect, self._colour)]
        else:
            for subtree in self._subtrees:
                gr_list.extend(subtree.get_rectangles())
            return gr_list

    # **************************************************************************
    # **************** TASK 3: GET_TREE_AT_POSITION ****************************
    # **************************************************************************

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Returns the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        """
        if not self._subtrees:
            x, y, width, height = self.rect
            if (x <= pos[0] <= x + width) and (y <= pos[1] <= y + height):
                return self
            else:
                return None
        elif not self._expanded:
            x, y, width, height = self.rect
            if (x <= pos[0] <= x + width) and (y <= pos[1] <= y + height):
                return self
            else:
                return None
        else:
            correct_tree = None
            for subtree in self._subtrees:
                selected_tree = subtree.get_tree_at_position(pos)
                if selected_tree:
                    correct_tree = selected_tree
            return correct_tree

    # **************************************************************************
    # ********* TASK 4: MOVE, CHANGE SIZE, DELETE, UPDATE SIZES ****************
    # **************************************************************************

    def update_data_sizes(self) -> int:
        """Updates the data_size attribute for this tree and all its subtrees,
        based on the size of their leaves, and return the new size of the given
        tree node after updating.

        If this tree is a leaf, return its size unchanged.
        """
        if not self._subtrees:
            return self.data_size
        else:
            updated_ds = 0
            for subtree in self._subtrees:
                updated_ds += subtree.update_data_sizes()
            self.data_size = updated_ds
            return self.data_size

    def change_size(self, factor: float) -> None:
        """Changes the value of this tree's data_size attribute by <factor>.
        Always rounds up the amount to change, so that it's an int, and
        some change is made. If the tree is not a leaf, this method does
        nothing.
        """
        #
        if not self._subtrees:
            change = math.ceil(abs(self.data_size * factor))
            if factor <= 0:
                self.data_size += -change
            elif factor > 0:
                self.data_size += change
            if self.data_size < 0:
                self.data_size = 1

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful. Only do this if this node
        has a parent tree.

        Do not set self._parent_tree to None, because it might be used
        by the visualizer to go back to the parent folder.
        """
        #
        if len(self._parent_tree._subtrees) == 1:
            if self._parent_tree is not None:
                self._parent_tree._subtrees.remove(self)
                self._parent_tree.delete_self()
        else:
            if self._parent_tree is not None:
                self._parent_tree._subtrees.remove(self)
                return True
        return False

    # **************************************************************************
    # ************* TASK 5: UPDATE_COLOURS_AND_DEPTHS **************************
    # **************************************************************************

    def update_depths(self) -> None:
        """Updates the depths of the nodes, starting with a depth of 0 at this
        tree node.
        """
        if self._parent_tree is None:
            self._depth = 0
            for subtree in self._subtrees:
                subtree.update_depths()
            return None
        elif not self._subtrees:
            current_depth = self._parent_tree._depth + 1
            self._depth = current_depth
            return None
        else:
            current_depth = self._parent_tree._depth + 1
            self._depth = current_depth
            for subtree in self._subtrees:
                subtree.update_depths()
            return None

    def max_depth(self) -> int:
        """Returns the maximum depth of the tree, which is the maximum length
        between a leaf node and the root node.
        """
        if not self._subtrees:
            return self._depth
        else:
            max_depth = 0
            for subtree in self._subtrees:
                curr_depth = subtree.max_depth()
                max_depth = max(max_depth, curr_depth)
            return max_depth

    def update_colours(self, step_size: int) -> None:
        """Updates the colours so that the internal tree nodes are
        shades of grey depending on their depth. The root node will be black
        (0, 0, 0) and all internal nodes will be shades of grey depending on
        their depth, where the step size determines the shade of grey.
        Leaf nodes should not be updated.
        """
        if self._parent_tree is None:
            self._colour = (0, 0, 0)
            for subtree in self._subtrees:
                subtree.update_colours(step_size)
        elif not self._subtrees:
            return None
        else:
            new_step = step_size * self._depth
            new_colour = (new_step, new_step, new_step)
            self._colour = new_colour
            for subtree in self._subtrees:
                subtree.update_colours(step_size)
        return None

    def update_colours_and_depths(self) -> None:
        """This method is called any time the tree is manipulated or right after
        instantiation. Updates the _depth and _colour attributes throughout
        the tree.
        """
        # 1. Call the update depths method you wrote.
        self.update_depths()
        # 2. Find the maximum depth of the tree.
        maximum_depth = self.max_depth() - 1
        # 3. Use the maximum depth to determine the step_size.
        step_size = math.ceil(200 / maximum_depth)
        # 4. Call the update_colours method and use step_size as the parameter.
        self.update_colours(step_size)

    # **************************************************************************
    # ********* TASK 6: EXPAND, COLLAPSE, EXPAND ALL, COLLAPSE ALL *************
    # **************************************************************************

    def expand(self) -> None:
        """Sets this tree to be expanded. But not if it is a leaf.
        """
        if not self._subtrees:
            return None
        else:
            self._expanded = True
            return None

    def expand_all(self) -> None:
        """Sets this tree and all its descendants to be expanded, apart from the
        leaf nodes.
        """
        if not self._subtrees:
            return None
        else:
            self._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()
            return None

    def collapse(self) -> None:
        """Collapses the parent tree of the given tree node and also collapse
        all of its descendants.
        """
        if self._parent_tree is None:
            for subtree in self._subtrees:
                subtree.collapse()
        else:
            self._parent_tree._expanded = False
            for subtree in self._subtrees:
                subtree.collapse()

    def collapse_all(self) -> None:
        """ Collapses ALL nodes in the tree.
        """
        self.collapse()
        if self._parent_tree is not None:
            self._parent_tree.collapse_all()

    # **************************************************************************
    # ************* TASK 7 : DUPLICATE MOVE COPY_PASTE *************************
    # **************************************************************************

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, moves this
        tree to be the last subtree of <destination>. Otherwise, does nothing.
        """
        if (not self._subtrees) and destination._subtrees != []:
            self._parent_tree._subtrees.remove(self)
            destination._subtrees.append(self)
            self._parent_tree = destination

    def duplicate(self) -> Optional[TMTree]:
        """Duplicates the given tree, if it is a leaf node. It stores
        the new tree with the same parent as the given leaf. Returns the
        new node. If the given tree is not a leaf, does nothing.
        """
        #
        if not self._subtrees:
            path_str = self.get_full_path()
            duplicate_tree = FileSystemTree(path_str)
            self._parent_tree._subtrees.append(duplicate_tree)
            duplicate_tree._parent_tree = self._parent_tree
            return duplicate_tree
        return None
        # NOTES: - make good use of the FileSystemTree constructor to
        #          instantiate a new node.

    def copy_paste(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, this method
        copies the given, and moves the copy to the last subtree of
        <destination>. Otherwise, does nothing.
        """
        if (not self._subtrees) and destination._subtrees != []:
            path_str = self.get_full_path()
            duplicate_tree = FileSystemTree(path_str)
            destination._subtrees.append(duplicate_tree)
            duplicate_tree._parent_tree = destination

    # **************************************************************************
    # ************* HELPER FUNCTION FOR TESTING PURPOSES  **********************
    # **************************************************************************
    def tree_traversal(self) -> List[Tuple[str, int, Tuple[int, int, int]]]:
        """For testing purposes to see the depth and colour attributes for each
        internal node in the tree. Used for passing test case 5.
        """
        if len(self._subtrees) > 0:
            output_list = [(self._name, self._depth, self._colour)]
            for tree in self._subtrees:
                output_list += tree.tree_traversal()
            return output_list
        else:
            return []

    # **************************************************************************
    # *********** METHODS DEFINED FOR STRING REPRESENTATION  *******************
    # **************************************************************************
    def get_path_string(self) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                self.get_separator() + self._name

    def get_separator(self) -> str:
        """Returns the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Returns the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    # **************************************************************************
    # **************** HELPER FUNCTION FOR TASK 7  *****************************
    # **************************************************************************
    def get_full_path(self) -> str:
        """Returns the path attribute for this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.

    === Private Attributes ===
    _path: the path that was used to instantiate this tree.
    """
    _path: str

    def __init__(self, my_path: str) -> None:
        """Stores the directory given by <my_path> into a tree data structure
        using the TMTree class.

        Precondition: <my_path> is a valid path for this computer.
        """
        # 1. Initialize the single attribute: self._path
        self._path = my_path
        # 2. Implement the algorithm described in the handout.
        if not os.path.isdir(my_path):
            file_name = os.path.basename(self._path)
            file_size = os.path.getsize(self._path)
            TMTree.__init__(self, file_name, [], file_size)
        else:
            file_name = os.path.basename(self._path)
            file_size = os.path.getsize(self._path)
            # list of subtrees in str format
            file_subtrees = os.listdir(self._path)
            # of subtrees in tree format
            list_subtrees = []

            for sub_file in file_subtrees:
                new_path = os.path.join(my_path, sub_file)
                subtree = FileSystemTree(new_path)
                list_subtrees.append(subtree)

            TMTree.__init__(self, file_name, list_subtrees, file_size)

    def get_full_path(self) -> str:
        """Returns the file path for the tree object.
        """
        return self._path

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
