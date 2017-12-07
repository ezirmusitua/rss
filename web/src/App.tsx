import * as React from 'react';
import './App.css';

const content = '身为一个&nbsp;Nintendo&nbsp;Switch&nbsp;' +
    '玩家，为了能买到真正便宜的游戏，每次剁手之前我都会仔细对比一下各个地区&nbsp;eshop&nbsp;的价格。' +
    '另外，由于并不是所有区域的游戏都自带中文，每次都需要查一下游戏的语言支持情况。</p><p>于是我就想：' +
    '有没有一种方法可以知道目前某个游戏哪个地区的价格最低，并且能告诉我游戏是否支持中文呢？</p><p>在经过了一番搜索后，' +
    '我找到了这个名叫「switch游戏低价查询」小程序。</p><p>这个小程序的功能很简单。在搜索栏中输入你希望购买的游戏，' +
    '它就能告诉你目前该游戏的最低价格。不仅如此，它还会显示这个游戏哪个区支持中文，是否是&nbsp;Switch&nbsp;独占游戏。' +
    '所有的信息都一目了然，非常直观和方便。';

class App extends React.Component {
    openLink(link: string) {
        window.open(link, '__blank');
    }

    render() {
        return (
            <div className="app">
                <div className="app-header">
                    <h2>RSS Reader</h2>
                </div>
                <article className="articles-container">
                    <section className="articles-container__list-container">
                        {
                            [0, 1, 3, 4, 5].map(item =>
                                <section
                                    key={item}
                                    className="articles-container__list-item"
                                    onClick={e => this.openLink('https://sspai.com/post/42192')}
                                >
                                    <div>
                                        <p>如何在 eshop 买到最便宜的 Nintendo Switch 游戏?</p>
                                        <span>Thu, 07 Dec 2017 14:31:54</span>
                                    </div>
                                    <article
                                        className="article-item__content"
                                        dangerouslySetInnerHTML={{
                                            __html: content.replace(
                                                /(<? *script)/gi,
                                                'illegalscript'
                                            ) + ' ... '
                                        }}
                                    />
                                </section>)
                        }
                    </section>
                </article>
            </div>
        );
    }
}

export default App;
