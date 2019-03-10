#include "libexhsearch/location.h"

#include "gtest/gtest.h"

using namespace graph;

TEST(LocationTest, OperatorPlusCorrectResult) {
	Location origin(3, 4);
	Location::OffsetType offset(-4, 1);
	auto new_location = origin + offset;
	EXPECT_EQ(-1, new_location.getRow()) << "Wrong row result for operator+.";
	EXPECT_EQ(5, new_location.getColumn()) << "Wrong column result for operator+.";
}

TEST(LocationTest, OperatorPlusKeepsOriginal) {
	Location origin(3, 4);
	Location::OffsetType offset(-5, -3);
	auto new_location = origin + offset;
	EXPECT_EQ(3, origin.getRow()) << "Row altered by operator+.";
	EXPECT_EQ(4, origin.getColumn()) << "Column altered by operator+.";
}

TEST(LocationTest, OperatorPlusInplaceAltersOriginal) {
	Location origin(3, 4);
	Location::OffsetType offset(1, -5);
	origin += offset;
	EXPECT_EQ(4, origin.getRow()) << "Wrong row result for operator+=.";
	EXPECT_EQ(-1, origin.getColumn()) << "Wrong column result for operator+=.";
}

TEST(LocationTest, OperatorPlusInplaceReturnsSelf) {
	Location origin(3, 4);
	Location::OffsetType offset(1, -5);
	auto & new_location = origin += offset;
	EXPECT_EQ(&new_location, &origin) << "operator+= does not return *this.";
}

TEST(LocationTest, OperatorEqualReturnsTrue) {
	Location firstLocation(3, 4);
	Location secondLocation(3, 4);
	EXPECT_TRUE(firstLocation == secondLocation) << "operator== has wrong result.";
	EXPECT_EQ(firstLocation, secondLocation) << "Gtest does not recognize equal locations.";
}

TEST(LocationTest, OperatorEqualReturnsFalse) {
	Location firstLocation(3, 1000);
	Location secondLocation(3, 4);
	EXPECT_FALSE(firstLocation == secondLocation) << "operator== has wrong result.";
	EXPECT_NE(firstLocation, secondLocation) << "Gtest does not recognize unequal locations.";
}

TEST(LocationTest, OperatorUnequalReturnsTrue) {
	Location firstLocation(3, 1000);
	Location secondLocation(3, 4);
	EXPECT_TRUE(firstLocation != secondLocation) << "operator== has wrong result.";
}

TEST(LocationTest, OperatorUnequalReturnsFalse) {
	Location firstLocation(3, 4);
	Location secondLocation(3, 4);
	EXPECT_FALSE(firstLocation != secondLocation) << "operator== has wrong result.";
}

TEST(LocationTest, GetRowReturnsRow) {
	Location location(3, 4);
	Location secondLocation(3, 4);
	EXPECT_EQ(location.getRow(), 3) << "getRow() does not return correct value.";
}

TEST(LocationTest, GetColumnReturnsColumn) {
	Location location(3, 4);
	Location secondLocation(3, 4);
	EXPECT_EQ(location.getColumn(), 4) << "getColumn() does not return correct value.";
}

TEST(LocationTest, OperatorLessThanDifferentRow) {
	Location first(-1, 4);
	Location second(3, 4);
	EXPECT_TRUE(first < second);
}

TEST(LocationTest, OperatorLessThanFalseDifferentRow) {
	Location first(7, 4);
	Location second(3, 4);
	EXPECT_FALSE(first < second);
}

TEST(LocationTest, OperatorLessThanEqualRow) {
	Location first(3, 4);
	Location second(3, 17);
	EXPECT_TRUE(first < second);
}

TEST(LocationTest, OperatorLessThanFalseEqualRow) {
	Location first(3, 4);
	Location second(3, -17);
	EXPECT_FALSE(first < second);
}