package database

import (
	"fmt"

	"github.com/makeok/go-web-init/pkg/config"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

func NewMysql(conf *config.DBConfig) (*gorm.DB, error) {
	//拼接下dsn参数, dsn格式可以参考上面的语法，这里使用Sprintf动态拼接dsn参数，因为一般数据库连接参数，我们都是保存在配置文件里面，需要从配置文件加载参数，然后拼接dsn。
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8&parseTime=True&loc=Local&timeout=%s", 
		conf.User, conf.Password, conf.Host, conf.Port, conf.Name, "3s")
	return gorm.Open(mysql.Open(dsn), &gorm.Config{})
}
