import * as React from 'react';
import './App.css';
import {ApolloClient, ApolloProvider, gql, graphql, createNetworkInterface} from 'react-apollo';


const client = new ApolloClient({
    networkInterface: createNetworkInterface({
        uri: 'http://localhost:3081/gql',
    })
} as any);

function replaceTag(content: string) {
    return content
        .replace(/(<? *script)/gi, 'illegalscript')
        .replace(/<figure .*?>.*?<\/figure.*?>/gi, '<image>')
        .replace(/<img .*?>/gi, '<image>')
        .concat(' ... ')
}

function convertToDate(tstamp: number) {

    const date = new Date(tstamp * 1000);
    const datevalues = [
        date.getFullYear(),
        date.getMonth() + 1,
        date.getDate(),
        date.getHours(),
        date.getMinutes(),
        date.getSeconds(),
    ];
    return datevalues.slice(0, 3).join('/') + ' ' + datevalues.slice(3).join(':');
}

interface Props {
    data: any;
}

class ArticleList extends React.Component<Props, object> {
    openLink(link: string) {
        window.open(link, '__blank');
    }

    render() {
        const {loading, error, articles} = this.props.data;
        if (loading) return <section> Loading Articles ... </section>;
        if (error) return <section> Error Happened ... </section>;
        return (<section className='articles-container__list-container'>
            {
                articles.map((item: any) =>
                    <section
                        key={item.hash}
                        className='articles-container__list-item'
                        onClick={e => this.openLink(item.link)}
                    >
                        <div>
                            <p>{item.title}</p>
                            <span>{convertToDate(item.publish_at)}</span>
                        </div>
                        <article
                            className='article-item__content'
                            dangerouslySetInnerHTML={{__html: replaceTag(item.description)}}
                        />
                    </section>)
            }
        </section>)
    }
}

const ArticleListWithData = graphql(gql`
query {
  articles {
    title
    link,
    hash,
    publish_at
    description
  }
}`)(ArticleList);

class App extends React.Component {
    render() {
        return (
            <ApolloProvider client={client}>
                <div className='app'>
                    <div className='app-header'>
                        <h2>RSS Reader</h2>
                    </div>
                    <article className='articles-container'>
                        <ArticleListWithData/>
                    </article>
                </div>
            </ApolloProvider>
        );
    }
}

export default App;
