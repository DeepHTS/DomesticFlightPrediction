import pandas as pd
import datetime
import math

class Plane:

    def __init__(self, data_path):
        columns = set(
            [
                "Dep Airport Code",
                "Arr Airport Code",
                "Effective From",
                "Effective To",
                "Local Dep Time",
                "Local Arr Time",
                "Flying Time",
            ]
        )
        timetable = pd.read_csv(data_path)
        timetable = timetable[timetable["International/Domestic"]=="Domestic"]
        self.timetable = pd.DataFrame({column:timetable[column] for column in columns})
        self.airport2point = {}
        self.date = datetime.date.today()
        self.margin = datetime.timedelta(minutes=10)
        self.threshold = 10

    
    def __len__(self):
        return len(self.timetable)

    
    def str2date(self, string):
        d, m, y = [int(i) for i in string.split("/")]
        t = datetime.date(y,m,d)
        return t


    def int2datetime(self, num):
        h = num//100
        m = num%100
        t = datetime.datetime.combine(self.date, datetime.time(h,m))
        return t


    def get_point(self, dep_time, arr_time, judge_datetime, dep_airport, arr_airport):
        """
        飛行機一機の座標を求める。
        線形計算。

        Args:
            dep_time(str):出発時刻
            arr_time(str):到着時刻
            judge_datetime(datetime):位置を知りたい時刻
            dep_airport(str):出発空港コード
            arr_airport(str):到着空港コード
        Returns:
            tuple(latitude:int, longitude:int):飛行機のjudge_timeにおける座標
        Note:
            judge_time時に空中にいなければNoneを返す。
        """
        dep_datetime = self.int2datetime(dep_time)
        arr_datetime = self.int2datetime(arr_time)

        if dep_datetime > arr_datetime:
            arr_datetime += datetime.timedelta(days=1)

        dep_datetime += self.margin
        arr_datetime -= self.margin

        if judge_datetime <= dep_datetime or arr_datetime <= judge_datetime or arr_datetime <= dep_datetime:
            return None

        return None

        dep_point = self.airport2point(dep_airport)
        arr_point = self.airport2point(arr_airport)

        point = ((arr_datetime - judge_datetime)*dep_point + (judge_datetime - dep_datetime)*arr_point) / (arr_datetime - dep_datetime)

        return point


    def dis_check(self, p1, p2):
        """
        2地点間の距離が閾値以下かどうかを判定

        Args:
        p1(tuple(int,int)):1つ目の地点の座標
        p2(tuple(int,int)):2つ目の地点の座標
        Returns:
        res(boolean):2地点間の距離が閾値以下かどうか
        以下ならTrue
        Note:
        地点が片方でもNoneならFalseを返す
        """
        if p1 is None or p2 is None:
            res = False
        else:
            res = (math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2) <= self.threshold)
        return res
  

    def density(self, judge_datetime, point):
        """
		csvの全データをget_point()で確認していき、中心座標から一定距離内に存在する機体の数を調べる。O(n)でn=200000なので2秒以内に実行可能。
			
		Args:
            judge_datetime(datetime):密度を知りたい時刻
            point(tuple(latitude:int, longitude:int)):密度を知りたい中心座標
        Returns:
            plane_num(int):中心座標から一定距離内に存在する機体の数
        """

        plane_num = 0

        for i in range(len(self)):
            plane_num+=1
            ef = datetime.datetime.combine(self.str2date(self.timetable["Effective From"].iloc[i]), datetime.time(0, 0))
            et = datetime.datetime.combine(self.str2date(self.timetable["Effective To"].iloc[i]), datetime.time(23, 59))
            if judge_datetime < ef or et < judge_datetime:
                continue
            dep_time = self.timetable["Local Dep Time"].iloc[i]
            arr_time = self.timetable["Local Arr Time"].iloc[i]
            dep_airport = self.timetable["Dep Airport Code"].iloc[i]
            arr_airport = self.timetable["Arr Airport Code"].iloc[i]
            
            if self.dis_check(self.get_point(dep_time, arr_time, judge_datetime, dep_airport, arr_airport), point):
                plane_num+=1

        return plane_num
